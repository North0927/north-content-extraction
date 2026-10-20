"""检查早派发任务单；只读，不发送消息、不分类、不拦截宿主工具。"""
import argparse
import json
import ntpath
from pathlib import Path
import re

POLICY = Path(__file__).resolve().parents[1] / 'references/policy.json'


def inside(child, parent):
    """检查Windows绝对路径的词法边界；真实连接与权限由宿主另验。"""
    if not isinstance(child, str) or not isinstance(parent, str):
        return False
    if not re.match(r'^[A-Za-z]:[\\/]', child) or not re.match(r'^[A-Za-z]:[\\/]', parent):
        return False
    c, p = ntpath.normcase(ntpath.normpath(child)), ntpath.normcase(ntpath.normpath(parent))
    try:
        return ntpath.commonpath([c, p]) == p
    except ValueError:
        return False


def check(task):
    policy = json.loads(POLICY.read_text(encoding='utf-8-sig'))
    errors = []
    if not isinstance(task, dict):
        return {'ok': False, 'errors': ['任务单必须为JSON对象']}
    fields = ('task_id', 'engine_version', 'revision', 'source_manifest_sha256',
              'project_id', 'project_root', 'target_thread_id', 'source', 'user_goal',
              'primary_domain', 'classification_basis', 'classification_status',
              'allowed_directory', 'content_directory', 'report_directory', 'analysis_owner')
    for key in fields:
        if not isinstance(task.get(key), str) or not task[key].strip():
            errors.append(key + '必须为非空字符串')
    if task.get('engine_version') != policy['version'] or task.get('revision') != policy['revision']:
        errors.append('引擎版本或修订与当前源不符')
    if not re.fullmatch(r'[0-9a-fA-F]{64}', str(task.get('source_manifest_sha256', ''))):
        errors.append('缺少有效源清单SHA-256；实际内容哈希需另行回读')
    if task.get('target_busy') is not False:
        errors.append('目标忙碌或状态未核验，先排队')
    if task.get('analysis_owner') != 'domain_worker':
        errors.append('早派发默认分析负责人必须为领域执行者')
    if task.get('scope_task_ids') != [task.get('task_id')]:
        errors.append('本任务单只授权一个当前任务，不包含历史待办')
    operations = task.get('dispatcher_pre_dispatch_operations')
    allowed = policy['coordination']['dispatcher_pre_dispatch_operations']
    if not isinstance(operations, list) or not all(isinstance(x, str) and x in allowed for x in operations):
        errors.append('统筹前置操作含媒体处理/分析或字段无效')
    if task.get('classification_status') not in ('confirmed', 'provisional'):
        errors.append('分类须明确已确认或临时；未分类先补必要依据')
    if task.get('mode') not in ('unknown', 'brief', 'detailed'):
        errors.append('模式须为unknown/brief/detailed')
    if task.get('media_status') not in ('unknown', 'partial', 'available', 'unavailable'):
        errors.append('媒体状态无效')
    duration = task.get('duration_seconds')
    if duration is not None and (isinstance(duration, bool) or not isinstance(duration, (int, float)) or
                                 duration < 0 or duration != duration or abs(duration) == float('inf')):
        errors.append('时长只能为有限非负秒数或null')
    for child, parent in [('allowed_directory', 'project_root'),
                          ('content_directory', 'allowed_directory'),
                          ('report_directory', 'content_directory')]:
        if not inside(task.get(child), task.get(parent)):
            errors.append(child + '必须在' + parent + '内且为绝对路径')
    return {'ok': not errors, 'errors': errors,
            'engine_version': policy['version'], 'revision': policy['revision'],
            'scope': '字段与角色约定检查；不是实际发送、语义分类或文件权限验收'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task_json')
    args = parser.parse_args()
    try:
        result = check(json.loads(Path(args.task_json).read_text(encoding='utf-8-sig')))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['ok'] else 1)


if __name__ == '__main__':
    main()
