# 安装与配置

## 交给 AI 助手

    请安装 https://github.com/North0927/north-content-extraction 完整引擎。
    检查同名版本和宿主能力，保留旧版及配置，说明位置。
    确认 SKILL.md 的相对资源全部可读。

没有接口就采用下载读取方式，不伪称安装成功。

## 下载读取

1. 在版本发布（Releases）下载 ZIP。
2. 按 SHA256SUMS.txt 核对，解压到自己的目录。
3. 将 SKILL.md 和目录访问权限交给助手，执行快速开始。

Windows 可用 Get-FileHash -LiteralPath '文件.zip' -Algorithm SHA256。哈希一致证明文件相同，不证明报告正确。

## 配置与工具

本包不直接调用服务，无额外 API 密钥。文字任务需要已有 AI 宿主、素材、目的与输出目录。

多执行者需真实接口和授权。dispatch_check.py 的 Windows 词法路径检查不是权限隔离。

可选 Python 3.10+ 用于策略工具。仅构建文档或渲染报告需要 Node.js 24.15+ 与 npm：

    npm ci --ignore-scripts
    npm run report -- examples/demo/report.md output/report.html

渲染器只将已有 Markdown 生成 HTML，不分析或调用模型；目标已存在时拒绝覆盖。

## 卸载

从宿主移除技能入口，再移除解压的引擎文件。用户素材、报告和配置另外保留，不连同工作区删除。
