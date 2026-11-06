# Third-party notices / 第三方素材与署名

本文件记录 Air China Fictional / B-38AC A380X 涂装使用的第三方素材、来源、处理方式与已有版权声明。记录日期：2026-11-06。

本项目是虚构的国航主题涂装，不声称获得中国国际航空、FlyByWire Simulations、Microsoft 或 Airbus 的联名、认可或素材再许可。此来源说明不向第三方标志、图像、机模或字体授予新的许可；它们原有的权利与适用条款不因转换成 SVG、PNG、XCF 或 DDS 而改变。本项目没有给所有内容统一指定 MIT、GPL 或其他通用许可。

## 1. 中国国际航空 / Air China 品牌素材

红凤凰、AIR CHINA 英文字标及中文“中国国际航空公司”题字为中国国际航空相关品牌标志；权利归相应权利人所有。涂装采用公开保存的矢量原件进行缩放、裁切与排版，没有将第三方标志重新声明为本项目原创。

| 本地文件 | 实际来源 | 本项目使用方式与原来源说明 |
| --- | --- | --- |
| `resources/airchina/airchina-full-lockup-companieslogo.svg` | [CompaniesLogo 国航页面](https://companieslogo.com/air-china/logo/)；[原始 SVG](https://companieslogo.com/img/orig/601111.SS_BIG-8bcf4a94.svg) | 从完整组合标志中裁出中文题字。CompaniesLogo 是第三方保存者；其页面说明标志属于各自权利人，展示用于编辑和信息用途。 |
| `resources/airchina/airchina-phoenix-companieslogo.svg` | [CompaniesLogo 国航页面](https://companieslogo.com/air-china/logo/)；[原始 SVG](https://companieslogo.com/img/orig/601111.SS-cd9d8fd2.svg) | 作为两侧尾翼凤凰，按尾翼方向布置。 |
| `resources/airchina/airchina-wordmark-commons.svg` | [Wikimedia Commons 文件页](https://commons.wikimedia.org/wiki/File:Air_China_wordmark.svg)；[原始 SVG](https://upload.wikimedia.org/wikipedia/commons/3/3b/Air_China_wordmark.svg) | 文件页作者列为 Air China Limited、来源列为 `www.airchina.us`；上游页面标注 `PD-shape`，同时保留商标提示。这里只转述该页面标记，不为其他国航图形指定相同状态。 |

品牌形状和实机布局另参考[国航官网品牌页](https://webresource.airchina.com.cn/zh-CN/content/about_us/civilization/logo/)及官网机队图片。参考图片、备用文件与完整采集 URL 记录在 [resources/airchina/SOURCES.md](resources/airchina/SOURCES.md)。官网照片没有作为机身贴图直接粘贴；公开仓库保留实际制作使用的三个 SVG 与来源记录，不重发整套网页和参考照片。

下载文件中的实际矢量填色仅用于本次虚构设计，不声明为经国航确认的官方喷漆标准。`B-38AC` 及本项目中的国航 A380 构图均为虚构内容。

## 2. FlyByWire Simulations：A380X 与 paintkit

基础 A380X 飞机由 FlyByWire Simulations 及其贡献者制作。本安装包通过配置引用用户另行安装的非模块化 Stable A380X，不包含完整飞机模型、系统或声音。

本项目制作使用官方 A380X paintkit 0.3 的 `A380X_PAINTKIT_V0.3.psd` 与 `A380X_PAINTKIT.obj`。原始 PSD 的底色、面板细节、门框、标记和做旧层被导出并参与最终图层合成；驾驶舱编号贴图改自基础飞机的 `A380X_REGISTRATION_ALBEDO.PNG.DDS`，保留透明背景与 SELCAL 等标签，仅更换机号文字。这些第三方成分也存在于最终 PNG/DDS 及可编辑 XCF 源文件中。

官方几何用于离线定位、UV 投影烘焙及预览。仓库和本项目源码附件不包含原始 paintkit PSD、OBJ/FBX、打包了其几何的 Blender 场景或提取的 `.npz` 几何缓存。预览图片是基于官方 paintkit 几何的离线渲染，仍然不是游戏内截图。

来源与上游资料：

- [FlyByWire 官方网站](https://flybywiresim.com/)
- [FlyByWireOfficial 发布的 A380X Paint Kit 0.3](https://flightsim.to/addon/83825/a380x-paint-kit)
- [FlyByWire aircraft 上游仓库](https://github.com/flybywiresim/aircraft)
- [上游 LICENSE](https://github.com/flybywiresim/aircraft/blob/master/LICENSE)

paintkit 发布页要求通过官方渠道取得原始文件，并禁止转载原始 paintkit。本文件记录实际来源与派生使用方式，不将该要求改写为转载原始包的授权，也不自行给 FBW 图形素材另授 MIT 或 GPL 许可。

`package/airchina-fbw-a380x-stable/SimObjects/AirPlanes/FlyByWire_A380_842_AirChina_Fictional/model.AIRCHINA/model.cfg` 中的以下原有声明继续保留：

```ini
; Copyright (c) 2023-2024 FlyByWire Simulations
; SPDX-License-Identifier: GPL-3.0
```

该文件级声明不为本项目中其他品牌标志或全部图形成分重新指定许可。

早期制作还参考了[官方 Native 2024 Livery Creator Package v1.1](https://flybywirecdn.com/addons/a380x/paintkit/A380X_Native_2024_Livery_Package_v1.1.zip)及[官方说明](https://flybywiresim.com/notams/development-update-native-msfs-2024-a380x/)。该 Native 模板、官方脚本原件及未编译工程不属于本次公开 Stable 安装包；取得和使用它们时应保留上游随附的声明及说明。

## 3. 字体、工具与本项目新增内容

机号等文字图层使用本机 Arial/Arial Bold 字体；中文品牌题字来自上述企业矢量，没有以普通中文字体替代。仓库与源码附件保存文字图层和渲染结果，不包含字体文件。重新生成文字需要相应本机字体，字体本身遵循权利人的条款。

制作使用 GIMP 与 Blender；本项目不附带这两个应用的可执行程序。工具名称仅记录制作流程，不表示工具开发者参与或背书涂装。

本项目另行完成了 A380 机身布局、腰线位置、虚构机号、图层组织与制作、导出和校验脚本。本说明是来源与署名记录，不是对新增代码或设计授予通用许可的 LICENSE；已有文件级版权与许可声明继续适用，第三方名称及商标归各自权利人所有。
