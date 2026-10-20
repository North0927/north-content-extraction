import {defineConfig} from "vitepress"
export default defineConfig({
  "lang": "zh-CN",
  "title": "North 内容提炼引擎",
  "description": "有来源、有步骤、有真实成果的中文 AI 能力",
  "base": "/north-content-extraction/",
  "lastUpdated": true,
  "cleanUrls": true,
  "themeConfig": {
    "nav": [
      {
        "text": "能力导航",
        "link": "https://north0927.github.io/north-ai/"
      },
      {
        "text": "使用手册",
        "link": "/guide/quickstart"
      },
      {
        "text": "真实案例",
        "link": "/showcase/"
      }
    ],
    "sidebar": [
      {
        "text": "阅读导航",
        "items": [
          {
            "text": "快速开始",
            "link": "/guide/quickstart"
          },
          {
            "text": "安装与配置",
            "link": "/guide/install"
          },
          {
            "text": "完整使用说明",
            "link": "/guide/usage"
          },
          {
            "text": "故障排查",
            "link": "/guide/troubleshooting"
          },
          {
            "text": "真实案例",
            "link": "/showcase/"
          },
          {
            "text": "示例报告",
            "link": "/showcase/report"
          },
          {
            "text": "版本更新",
            "link": "/changelog"
          },
          {
            "text": "升级与回退",
            "link": "/upgrade/"
          },
          {
            "text": "依赖与边界",
            "link": "/guide/compatibility"
          }
        ]
      }
    ],
    "search": {
      "provider": "local",
      "options": {
        "locales": {
          "root": {
            "translations": {
              "button": {
                "buttonText": "搜索文档",
                "buttonAriaLabel": "搜索文档"
              },
              "modal": {
                "noResultsText": "没有找到结果",
                "resetButtonTitle": "清除搜索",
                "displayDetails": "显示详细结果",
                "backButtonTitle": "返回",
                "footer": {
                  "selectText": "选择",
                  "navigateText": "切换",
                  "closeText": "关闭"
                }
              }
            }
          }
        }
      }
    },
    "outline": {
      "label": "本页目录"
    },
    "docFooter": {
      "prev": "上一页",
      "next": "下一页"
    },
    "lastUpdated": {
      "text": "最后更新"
    },
    "darkModeSwitchLabel": "切换明暗主题",
    "sidebarMenuLabel": "菜单",
    "returnToTopLabel": "返回顶部",
    "socialLinks": [
      {
        "icon": "github",
        "link": "https://github.com/North0927/north-content-extraction"
      }
    ],
    "footer": {
      "message": "MIT 许可 · 案例与运行边界按证据说明",
      "copyright": "Copyright © 2026 清醒的北"
    }
  }
})
