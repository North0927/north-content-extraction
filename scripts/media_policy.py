"""V2.3.2只读策略工具：判定模式/计划抽帧/统计单条整夹；不采集媒体或调用模型。"""
import argparse
import ctypes
import json
import math
import os
from pathlib import Path

POLICY_PATH = Path(__file__).resolve().parents[1] / "references/policy.json"

def load_policy():
    return json.loads(POLICY_PATH.read_text(encoding="utf-8-sig"))

def natural(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(name + "必须是非负整数字节数")
    return value

def decide(kind, duration_seconds, storage_bytes, *, allow_long_detail=False,
           brief=False, projected_additional_bytes=0, storage_complete=True):
    if kind not in {"video", "audio", "article", "note", "image"}:
        raise ValueError("未知材料类型")
    if duration_seconds is not None:
        if isinstance(duration_seconds, bool) or not isinstance(duration_seconds, (int, float)):
            raise ValueError("时长必须是有限非负秒数或未知")
        if not math.isfinite(duration_seconds) or duration_seconds < 0:
            raise ValueError("时长必须是有限非负秒数或未知")
    if storage_bytes is not None:
        natural(storage_bytes, "空间")
    natural(projected_additional_bytes, "预计新增空间")
    p = load_policy()
    s, v = p["storage"], p["video"]
    current = storage_bytes
    peak = None if current is None else current + projected_additional_bytes
    long_video = kind == "video" and duration_seconds is not None and duration_seconds > v["long_threshold_seconds"]
    reasons, alerts = [], []
    if long_video:
        alerts.append("【长视频＞3分钟】")
    if current is not None and current > s["warning_bytes"]:
        alerts.append("【存储＞100MB】")
    if current is not None and current > s["force_brief_bytes"]:
        alerts.append("【整夹＞300MB，强制简略】")
        reasons.append("measured_storage_over_300MB")
    elif peak is not None and peak > s["force_brief_bytes"]:
        alerts.append("【预计峰值＞300MB，转简略】")
        reasons.append("projected_storage_over_300MB")
    if current is None or not storage_complete:
        reasons.append("storage_not_fully_verified")
    if brief:
        reasons.append("user_requested_brief")
    if kind == "video" and duration_seconds is None:
        alerts.append("【时长待核验】")
        reasons.append("duration_unknown")
    elif kind == "video" and duration_seconds > v["default_brief_threshold_seconds"] and not allow_long_detail:
        reasons.append("over_5_minutes_defaults_to_brief")
    mode = "brief" if reasons else "detailed"
    times = []
    if mode == "detailed" and kind == "video":
        for segment in v["sampling_segments"]:
            upper = min(duration_seconds, segment["end_seconds"]) if segment["end_seconds"] is not None else duration_seconds
            t = segment["start_seconds"]
            while t < upper:
                times.append(t)
                t += segment["interval_seconds"]
    return {"engine_version": p["version"], "kind": kind,
            "duration_seconds": duration_seconds, "long_video": long_video,
            "default_brief_threshold_seconds": v["default_brief_threshold_seconds"],
            "analysis_mode": mode, "mode_reasons": reasons,
            "alerts": alerts, "storage_scope": s["scope"],
            "storage_bytes": current, "projected_peak_bytes": peak,
            "storage_MB": None if current is None else round(current / 1000000, 6),
            "storage_MiB": None if current is None else round(current / 1048576, 6),
            "baseline_frame_times_seconds": times, "baseline_frame_count": len(times),
            "semantic_extra_frames": "only_after_actual_audio_visual_alignment_and_budget_check",
            "actual_frames_extracted": False, "actual_media_verified": False}

def allocated_bytes(path):
    if os.name != "nt":
        return None
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    fn = kernel.GetCompressedFileSizeW
    fn.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_uint32)]
    fn.restype = ctypes.c_uint32
    high = ctypes.c_uint32()
    ctypes.set_last_error(0)
    low = fn(str(path), ctypes.byref(high))
    error = ctypes.get_last_error()
    if low == 0xFFFFFFFF and error:
        raise OSError(error, "无法取得磁盘占用")
    return (high.value << 32) | low

def inspect_folder(folder):
    root = Path(folder).absolute()
    if not root.is_dir() or root.is_symlink() or (root.stat().st_file_attributes & 0x400 if os.name == "nt" else False):
        raise ValueError("统计根目录必须是真实内容目录，不接受目录连接")
    errors, allocation_errors, seen = [], [], set()
    logical, allocated, files, aliases = 0, 0, 0, 0
    allocation_available = os.name == "nt"
    def walking_error(error):
        errors.append(str(error))
    for base, dirs, names in os.walk(root, followlinks=False, onerror=walking_error):
        for name in list(dirs):
            path = Path(base) / name
            try:
                st = path.lstat()
                if path.is_symlink() or (getattr(st, "st_file_attributes", 0) & 0x400):
                    errors.append("跳过目录连接，需核验归属：" + str(path))
                    dirs.remove(name)
            except OSError as error:
                errors.append(str(error))
                dirs.remove(name)
        for name in names:
            path = Path(base) / name
            try:
                st = path.lstat()
                if path.is_symlink() or (getattr(st, "st_file_attributes", 0) & 0x400):
                    errors.append("跳过文件连接，需核验归属：" + str(path))
                    continue
                files += 1
                identity = (st.st_dev, st.st_ino) if st.st_ino else (str(path),)
                if identity in seen:
                    aliases += 1
                    continue
                seen.add(identity)
                logical += st.st_size
                try:
                    disk = allocated_bytes(path)
                    if disk is None:
                        allocation_available = False
                    else:
                        allocated += disk
                except OSError as error:
                    allocation_available = False
                    allocation_errors.append(str(error))
            except OSError as error:
                errors.append(str(error))
    gate = max(logical, allocated) if allocation_available else logical
    return {"folder": str(root), "scope": "single_content_entire_folder",
            "file_count": files, "unique_file_count": len(seen), "hardlink_alias_count": aliases,
            "logical_bytes": logical, "allocated_bytes": allocated if allocation_available else None,
            "gate_bytes": gate, "gate_MB": round(gate / 1000000, 6), "gate_MiB": round(gate / 1048576, 6),
            "measure": "max_logical_allocated" if allocation_available else "logical_only_fallback",
            "complete": not errors, "errors": errors, "allocation_errors": allocation_errors,
            "external_exclusive_staging_bytes_included": False}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    storage = sub.add_parser("storage", help="只读统计单条目录")
    storage.add_argument("folder")
    plan = sub.add_parser("plan", help="仅输出模式和取帧计划，不执行采集")
    plan.add_argument("--kind", choices=["video", "audio", "article", "note", "image"], required=True)
    plan.add_argument("--duration", type=float)
    group = plan.add_mutually_exclusive_group()
    group.add_argument("--folder")
    group.add_argument("--storage-bytes", type=int)
    plan.add_argument("--exclusive-staging-bytes", type=int, default=0)
    plan.add_argument("--projected-additional-bytes", type=int, default=0)
    plan.add_argument("--allow-long-detail", action="store_true", help="仅当用户明确授权该超过5分钟的视频详细分析时使用")
    plan.add_argument("--brief", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "storage":
            result = inspect_folder(args.folder)
        else:
            natural(args.exclusive_staging_bytes, "专属外置暂存")
            measurement = inspect_folder(args.folder) if args.folder else None
            size = measurement["gate_bytes"] if measurement else args.storage_bytes
            if size is not None:
                size += args.exclusive_staging_bytes
            result = decide(args.kind, args.duration, size, allow_long_detail=args.allow_long_detail,
                            brief=args.brief, projected_additional_bytes=args.projected_additional_bytes,
                            storage_complete=measurement["complete"] if measurement else True)
            result["folder_measurement"] = measurement
            result["exclusive_staging_bytes"] = args.exclusive_staging_bytes
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError) as error:
        parser.error(str(error))

if __name__ == "__main__":
    main()
