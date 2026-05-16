# MyGeoserverProject

基于 OpenLayers + GeoServer + PostGIS + Django 的 WebGIS 全栈应用。

## 项目架构

```
MyGeoserverProject/
├── frontend/                          # 前端静态页面
│   └── HTML/                          # OpenLayers 地图页面集合
│       ├── GeoserverOL.HTML           # 核心：查看/增/改/删 要素编辑器（Django 代理模式）
│       ├── QueryFeatureOL.HTML        # 查看：WMS GetFeatureInfo 矢量要素查询
│       ├── LoadTileMap.HTML           # 展示：WMS 瓦片地图加载
│       ├── FeatureOL.HTML             # 基础：矢量要素渲染示例（点/线/面）
│       ├── DrawOL.HTML                # 基础：OpenLayers Draw 绘制交互
│       ├── ModifyOL.HTML              # 基础：绘制/修改/选择要素交互
│       ├── CreateGMLOL.HTML           # 基础：WFS-T GML 生成器
│       └── ol/                        # OpenLayers 库文件及样式
│           ├── ol.js
│           ├── ol.css
│           ├── ol.css.map / ol.js.map
│           └── datav-style.css
│
├── backend/                           # Django 后端代理服务
│   └── gismap/
│       ├── gismap/
│       │   ├── settings.py            # Django 配置
│       │   ├── urls.py                # URL 路由映射
│       │   ├── geoserver.py           # 核心：GeoServer 代理视图（WMS/WFS 请求转发）
│       │   ├── templates/
│       │   │   └── GeoserverOL.html   # Django 模板版要素编辑器
│       │   └── static_files/          # 静态资源（ol.js, jQuery 等）
│       └── manage.py                  # Django 管理脚本
│
├── gis-infra/                         # GIS 基础设施
│   ├── docker-compose.yml             # Docker Compose：PostGIS + GeoServer 一键部署
│   ├── web.xml                        # 自定义 Tomcat 配置（含 CORS）
│   ├── fonts/                         # 字体挂载目录
│   ├── postgis-data/                  # PostGIS 数据持久化目录
│   └── geoserver-data/                # GeoServer 数据目录
│       ├── workspaces/
│       │   └── mapgis/                # mapgis 工作空间
│       │       ├── namespace.xml
│       │       ├── workspace.xml
│       │       ├── postgis/           # PostGIS 数据存储
│       │       │   ├── datastore.xml
│       │       │   └── v6_time_cnty_pts_utf_wgs84/       # 县级点图层
│       │       │   └── v6_time_pref_pgn_utf_wgs84_geoserver/  # 县级面图层（主要图层）
│       │       └── styles/
│       │           └── poi.sld / poi.xml
│       ├── styles/                    # 默认样式
│       ├── security/                  # 安全配置
│       └── gwc-layers/                # GeoWebCache 缓存配置
│
└── python/                            # 数据预处理脚本
    ├── cnty_pts_shptotxt.py           # 县级点 shapefile → 文本
    ├── cnty_pts_txttopg.py            # 县级点 文本 → PostGIS
    ├── pref_pgn_shptotxt.py           # 县级面 shapefile → 文本
    ├── pref_pgn_txttopg.py            # 县级面 文本 → PostGIS
    ├── pref_pts_shptotxt.py           # 县级点(面数据) shapefile → 文本
    └── pref_pts_txttopg.py            # 县级点(面数据) 文本 → PostGIS
```

## 技术栈

| 层级 | 技术 |
|------|------|
| **前端地图** | OpenLayers 4+ |
| **前端脚本** | jQuery 1.7.2 |
| **后端代理** | Django 4.2 |
| **地图服务** | GeoServer (kartoza/geoserver Docker 镜像) |
| **空间数据库** | PostGIS 16-3.4 (postgis/postgis Docker 镜像) |
| **容器化** | Docker Compose |
| **数据格式** | WMS (GetMap / GetFeatureInfo), WFS-T (Transaction) |

## 快速开始

### 1. 启动基础设施（Docker）

```bash
cd gis-infra
docker-compose up -d
```

这会启动两个容器：
- **PostGIS**（端口 5433）：空间数据库
- **GeoServer**（端口 8084）：地图服务

GeoServer 管理界面：http://localhost:8084/geoserver/web/  
默认账户：`admin` / `164523`

### 2. 启动 Django 后端

```bash
cd backend/gismap
python manage.py runserver 8080
```

Django 服务启动在：http://localhost:8080/

### 3. 访问前端页面

直接打开 HTML 文件访问：

| 文件 | 功能 | 访问方式 |
|------|------|---------|
| `GeoserverOL.HTML` | 查看/增/改/删 要素编辑器 | 直接打开或通过 Django |
| `QueryFeatureOL.HTML` | WMS GetFeatureInfo 要素查询 | 直接打开 |
| `LoadTileMap.HTML` | WMS 瓦片地图展示 | 直接打开 |
| `FeatureOL.HTML` | 矢量要素渲染示例 | 直接打开 |
| `DrawOL.HTML` | 绘制交互 | 直接打开 |
| `ModifyOL.HTML` | 绘制/修改/选择 | 直接打开 |
| `CreateGMLOL.HTML` | WFS-T GML 生成 | 直接打开 |

通过 Django 服务访问（推荐，可解决 CORS 问题）：  
http://localhost:8080/geoserver/ → GeoserverOL.html（Django 模板版）

### 4. 数据导入

使用 `python/` 目录下的脚本将 GIS 数据导入 PostGIS：

```bash
# 示例：将县级面数据导入 PostGIS
python python/pref_pgn_txttopg.py
```

## 核心功能

### 地图查看与查询
- 高德地图/腾讯地图作为底图
- WMS 矢量图层叠加显示
- 点击地图要素通过 GetFeatureInfo 查询属性
- 属性数据以表格形式展示

### 要素编辑（WFS-T）
- **增加**：绘制新要素并录入属性
- **修改**：选中要素后编辑几何和属性
- **删除**：选择要素从数据源移除
- 通过 WFS-T Transaction 协议提交变更到 GeoServer

### 数据流

```
[浏览器] ←→ [Django 代理] ←→ [GeoServer] ←→ [PostGIS]
    ↑              ↑
    └── 前端 HTML  └── 代理模式避免 CORS 问题
```

## 项目配置

### GeoServer 配置

- **工作空间**：`mapgis`（URI: http://geoserver/mapgis）
- **数据存储**：PostGIS 数据库连接
- **图层**：
  - `mapgis:v6_time_pref_pgn_utf_wgs84_geoserver`（县级面数据）
  - `mapgis:v6_time_cnty_pts_utf_wgs84`（县级点数据）
- **端口映射**：`8084:8080`

### Django 代理

[geoserver.py](backend/gismap/gismap/geoserver.py) 提供以下代理接口：

| 路由 | 方法 | 功能 |
|------|------|------|
| `/getfeature/` | GET | 代理 WMS GetFeatureInfo 请求 |
| `/getwmts/` | GET | 代理 WMS GetMap 请求 |
| `/wfs/` | POST | 代理 WFS-T Transaction 请求 |
| `/geoserver/` | GET | 渲染 GeoserverOL 模板页面 |

## 常见问题

### CORS 跨域问题
- **Django 代理模式**（推荐）：通过 `/getfeature/`、`/wfs/` 等路由转发请求，避免跨域
- **直接请求模式**：GeoServer 已配置 CORS 过滤器（web.xml），支持跨域访问

### 单击查询失败
- 确认 GET 请求 URL 中工作空间名正确（`mapgis` 而非 `gismap`）
- 确认 GeoServer 服务正常运行（http://localhost:8084/geoserver/web/）
- 确认 BBOX 范围能覆盖到面要素（EPSG:3857 下建议 BBOX 半宽 ≥ 100 米）

## License

MIT
