# MyGeoserverProject

基于 OpenLayers + GeoServer + PostGIS 的 WebGIS 历史地图全栈应用，支持中国历史行政区划（CHGIS）时间轴可视化与要素编辑。

## 项目架构

```
MyGeoserverProject/
├── frontend/                              # 前端 — TypeScript + Vite + OpenLayers 10
│   ├── index.html                         # 入口页面
│   ├── src/
│   │   ├── main.ts                        # 核心：地图初始化、WFS-T 编辑、时间轴控制
│   │   ├── timeline.ts                    # 时间轴 UI 控件（滑块/动画/朝代标记）
│   │   ├── timeline.css                   # 时间轴样式
│   │   ├── history.ts                     # 撤销/重做（Command 模式）
│   │   ├── declarations.d.ts              # TypeScript 类型声明
│   │   └── utils/
│   │       ├── style.ts                   # 要素样式函数
│   │       └── wfst.ts                    # WFS-T 事务序列化
│   ├── public/
│   │   └── datav-style.css                # DataV 风格全局样式
│   ├── HTML/                              # 旧版 HTML 页面集合（保留参考）
│   │   ├── GeoserverOL.HTML               # 要素编辑器（旧版）
│   │   ├── QueryFeatureOL.HTML            # GetFeatureInfo 查询
│   │   ├── LoadTileMap.HTML               # WMS 瓦片加载
│   │   ├── FeatureOL.HTML                 # 矢量渲染示例
│   │   ├── DrawOL.HTML                    # 绘制交互
│   │   ├── ModifyOL.HTML                  # 绘制/修改/选择
│   │   ├── CreateGMLOL.HTML               # WFS-T GML 生成器
│   │   └── ol/                            # OpenLayers 库及样式
│   ├── package.json
│   └── vite.config.js
│
├── gis-infra/                             # GIS 基础设施
│   ├── docker-compose.yml                 # Docker Compose：PostGIS + GeoServer
│   ├── web.xml                            # Tomcat CORS 配置
│   ├── fonts/                             # 字体挂载
│   ├── postgis-data/                      # PostGIS 数据持久化
│   └── geoserver-data/                    # GeoServer 数据目录
│       ├── workspaces/mapgis/
│       │   ├── postgis/
│       │   │   ├── datastore.xml
│       │   │   ├── v6_time_pref_pgn_utf_wgs84_geoserver/   # 县级面图层（主图层）
│       │   │   ├── v6_time_pref_pgn_timeline/              # 时间轴 SQL 视图
│       │   │   └── v6_time_cnty_pts_utf_wgs84/             # 县级点图层
│       │   └── styles/
│       ├── gwc-layers/                    # GeoWebCache 缓存
│       ├── security/
│       └── gwc/
│
├── python/                                # 数据预处理脚本
│   ├── pref_pgn_shptotxt.py              # 县级面 shapefile → 文本
│   ├── pref_pgn_txttopg.py               # 县级面 文本 → PostGIS
│   ├── cnty_pts_shptotxt.py              # 县级点 shapefile → 文本
│   ├── cnty_pts_txttopg.py               # 县级点 文本 → PostGIS
│   ├── pref_pts_shptotxt.py              # 县级点(面) shapefile → 文本
│   └── pref_pts_txttopg.py               # 县级点(面) 文本 → PostGIS
│
└── data/                                  # 原始 GIS 数据
    └── V6 Time Series Prefecture Polygons/
```
## 项目截图
<img width="3072" height="1644" alt="屏幕截图 2026-05-16 124609" src="https://github.com/user-attachments/assets/6d68747b-2721-4609-b370-2c88796cd844" />


## 技术栈

| 层级 | 技术 |
|------|------|
| **前端框架** | TypeScript 6 + Vite 8 |
| **地图引擎** | OpenLayers 10.9 |
| **DOM 操作** | jQuery 4 |
| **地图服务** | GeoServer 2.28 (kartoza/geoserver) |
| **空间数据库** | PostGIS 16-3.4 (postgis/postgis) |
| **容器化** | Docker Compose |
| **数据协议** | WMS (GetMap/GetFeatureInfo), WFS-T (Transaction) |
| **时间过滤** | CQL_FILTER (GeoServer CQL) |

## 快速开始

### 1. 启动基础设施

```bash
cd gis-infra
docker-compose up -d
```

启动两个容器：
- **PostGIS**（端口 5433）：空间数据库
- **GeoServer**（端口 8084）：地图服务

GeoServer 管理界面：http://localhost:8084/geoserver/web/  
默认账户：`admin` / `164523`

### 2. 导入数据

```bash
# 将县级面 shapefile 数据导入 PostGIS
python python/pref_pgn_txttopg.py
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

开发服务器：http://localhost:5173/

### 4. 构建生产版本

```bash
npm run build     # 输出到 frontend/dist/
npm run preview   # 预览构建结果
```

## 核心功能

### 历史时间轴（CHGIS）

- 数据源自 Harvard CHGIS V6 中国历史行政区划数据集
- 时间范围：公元前 224 年 — 公元 1911 年（秦至清末）
- 通过 CQL_FILTER 动态筛选 `beg_yr ≤ 年份 ≤ end_yr` 的行政区划
- 滑块拖动选择年份（150ms 防抖）、朝代标记快捷跳转、动画自动播放（1x/2x/5x 速度）
- 淡入淡出过渡效果，平滑切换不同年份的 WMS 图层

### 地图查看与查询

- 腾讯地图作为底图
- WMS 矢量图层叠加显示
- 搜索模式下点击地图，通过 GetFeatureInfo 查询要素属性
- 属性数据以表格形式展示

### 要素编辑（WFS-T）

- **查看**：点击 WMS 图层查询要素属性
- **增加**：绘制新要素（支持点/线/面/圆）并录入属性
- **修改**：选中要素后拖拽编辑几何形状，修改属性
- **删除**：选中要素从数据源移除
- 支持撤销/重做（Ctrl+Z / Ctrl+Y，Command 模式）
- 可选吸附（Snap）功能
- 通过 WFS-T Transaction 协议提交变更

### 数据流

```
[浏览器] ←→ [GeoServer:8084] ←→ [PostGIS:5433]
    ↑
    └── WMS GetMap (CQL_FILTER) / WFS-T Transaction

时间轴流程：
拖动滑块 → onChange(year) → ImageWMS + CQL_FILTER → GeoServer → PostGIS WHERE beg_yr/end_yr → PNG 返回
```

## 项目配置

### GeoServer 配置

| 项目 | 值 |
|------|-----|
| 工作空间 | `mapgis` |
| 数据存储 | PostGIS (host=postgis, port=5432, db=gis) |
| 主图层 | `mapgis:v6_time_pref_pgn_utf_wgs84_geoserver`（40,895 行） |
| 时间轴图层 | 同上，通过 CQL_FILTER 动态过滤 |
| 点图层 | `mapgis:v6_time_cnty_pts_utf_wgs84` |
| 端口映射 | `8084:8080` |

### 前端配置

| 项目 | 值 |
|------|-----|
| 默认底图 | 腾讯地图矢量瓦片 |
| 投影 | EPSG:4326 (axisOrientation: enu) |
| WMS 版本 | 1.1.0 |
| 时间轴范围 | -224 ~ 1911 |
| 动画速度 | 1x(800ms) / 2x(400ms) / 5x(160ms) |

## 常见问题

### 时间轴始终显示相同数据

确认 GeoServer 日志中 WMS 请求包含 `CQL_FILTER=beg_yr <= ... AND end_yr >= ...` 参数。若缺失，检查前端 `main.ts` 中 `createTimelineSource` 的 `CQL_FILTER` 参数是否正确配置。

### CORS 跨域

GeoServer 已配置 `DISABLE_CORS=true` 和自定义 `web.xml` CORS 过滤器，前端可直接请求 `localhost:8084`。

### 单击查询失败

- 确保在"查看"模式下点击地图
- 确认 GeoServer 服务运行正常（http://localhost:8084/geoserver/web/）
- 确认工作空间名为 `mapgis`，图层名正确

## License

MIT
