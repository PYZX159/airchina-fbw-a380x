FlyByWire A380X — 中国国际航空虚构涂装
Air China Fictional / B-38AC

版本 0.1.1
补齐首版遗漏的 9 个 .DDS.json 贴图描述文件并重新生成 layout.json。
针对用户首次游戏测试中出现的粉紫棋盘格加载问题，贴图像素保持不变。
此修正版已由用户完成 Microsoft Flight Simulator 2024 游戏内测试并确认发布。
请完全退出模拟器后，以本文件夹覆盖旧版同名涂装文件夹，再启动模拟器。

适用版本
本包面向非原生、非模块化的 FlyByWire A380X Stable 2024.1.0。
基础机模的 SimObjects 容器应为 FlyByWire_A380_842。
这是虚构国航 A380 涂装；B-38AC 是虚构注册号。
更新为较新的 Native 2024 模块化 A380X 后，请使用另行编译的 Native 涂装版本。

安装
1. 退出微软模拟飞行 2024。
2. 确认正在使用的 MSFS 2024 插件目录，而不是根据名称猜测目录。
   这台电脑的 UserCfg.opt 当前记录：
     InstalledPackagesPath "D:\Microsoft Flight Simulator 2024(ChaJian)"
   但发现的 A380X Stable 实际位于：
     D:\Microsoft Flight Simulator 2024(ChaJian)\Community2024
   同时存在 Community 和 Community2024，因此请通过当前插件管理器或
   FlyByWire Installer 的 MSFS 2024 目标设置，确认本次启动实际加载的目录。
3. 将整个 airchina-fbw-a380x-stable 文件夹复制到实际启用的 Community 目录。
   直接打开复制后的文件夹应能看见 manifest.json、layout.json 和 SimObjects。
   不要只复制 texture.AIRCHINA，不要复制 project 或 resources，不要覆盖基础机模。
4. 启动模拟器，选择 FlyByWire A380X，并在涂装列表选择：
     Air China Fictional - B-38AC

注册号
外部 B-38AC 直接绘制在机身贴图中，atc_id_enable=0 用来关闭额外动态机身编号。
注册号纹理 A380X_REGISTRATION_ALBEDO.PNG.DDS 在本机模型中用于驾驶舱铭牌，
其注册号改为 B-38AC，并保留 SELCAL 等其他标记。

卸载
退出模拟器，移除独立的 airchina-fbw-a380x-stable 涂装文件夹即可。
保留 flybywire-aircraft-a380-842 基础机模。

验证范围
文件结构、DDS 头、贴图尺寸、mipmap 与基础机模引用可通过制作工作区中的只读
Validate-Package.ps1 检查。本版另经用户完成 MSFS 2024 游戏内测试并确认发布。
随工作区保留的 Native 2024 工程尚未编译，不属于此 Stable 安装包。

来源
基于 FlyByWire 官方绘画套件与公开涂装工程。
官方资源：https://flybywiresim.com/notams/development-update-native-msfs-2024-a380x/
本包只包含涂装及其配置，不包含基础机模、系统或声音。
