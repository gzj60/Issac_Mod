# Player Homing Tears

一个为《The Binding of Isaac: Rebirth》Lua Mod 版本制作的弹道强化 Mod。

## 功能

- 玩家及友方跟班发射的泪弹会主动追踪最近的有效敌人。
- 玩家泪弹获得穿透和灵体效果，可以穿过敌人与障碍物。
- 泪弹保留角色当前的原生射程，不会被强制改为无限射程。
- 玩家及友方跟班发射的激光获得强追踪、穿透、灵体和无限距离效果。
- 敌人的泪弹、投射物和激光不会被修改。

## 安装

1. 下载或克隆本仓库。
2. 将 `player_homing_tears` 文件夹复制到游戏的 `mods` 目录。
3. 确认最终文件路径类似：

   ```text
   E:\SteamLibrary\steamapps\common\The Binding of Isaac Rebirth\mods\player_homing_tears\main.lua
   ```

4. 启动游戏，在 Mods 菜单中启用 **Player Homing Tears**。

> 需要支持 Lua Mod API 的游戏版本。

## 项目结构

```text
player_homing_tears/
  main.lua       Mod 主逻辑
  metadata.xml   Mod 名称、版本及说明
tests/           自动化检查
```

## 开发与测试

在仓库根目录运行：

```powershell
python -m pytest -q
```

当前 Mod 版本：`1.3`
