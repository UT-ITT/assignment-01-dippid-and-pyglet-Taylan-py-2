This is just the Readme for the game, the dippid sender is more or less self-explanatory.

# 👾 Face Invaders

Welcome to **Face Invaders**

If you think the game isn’t pretty…
**maybe take a look in the mirror first.** 😉

---

## 🎮 About the Game

Face Invaders is a chaotic, arcade-style shooter inspired by classic space invader games — but with a twist:

* Enemies? Faces.
* Player? Also a face.
* Bullets? Questionable characters.
* Dignity? Optional.

You control your character by tilting your phone and firing with the button input (via the DIPPI app). Survive waves of increasingly aggressive enemies while protecting yourself with bunkers.

---

## 📱 IMPORTANT: How to Play

🚨 **You MUST hold your phone horizontally (landscape mode)** 🚨
If you don’t… well… things will go very wrong very quickly.

---

## 🕹 Controls

* **Tilt phone while holding horizontally (left/right)** → Move player
* **Button press** → Shoot
* **Mouse click (on death screen)** → Respawn or Quit

---

## 📦 Requirements / Packages Used

Make sure you have the following Python packages installed:

```bash
pip install pyglet
```

### Built-in Python modules used:

* `random`
* `os`
* `time`
* `math`

### External dependency:

* `DIPPID` (for sensor input via UDP)

  * Provides accelerometer + button input from your device

---

## 📁 Project Structure

```
face_invaders/
│
├── main.py
├── sprites/
│   └── cutout/
│       ├── img_mouth_closed.png
│       ├── img_mouth_open.png
│       ├── img_ta_1.png
│       ├── img_ta_2.png
│       ├── img_prof.png
│       └── img_player_dead.png
│
├── sounds/
│   ├── pew.wav
│   ├── ohnoooo.wav
│   ├── destroy.wav
│   └── TempleOS_Hymn-Risen.wav
```

---

## 🔊 Features

* 🎵 Background music + sound effects voiced by me hehehe
* 👾 Multiple enemy types (you are the enemies since you guys are the TA's giving me difficult exercises, then i don't sleep enough)
* 🧱 Destructible bunkers (they respawn after some time!)
* 🌌 Animated starfield background (pretty cool huh)
* 📈 Increasing difficulty per level
* 💀 ohnooo sound effect when dead

---

## ⚠️ Known Issues

* Excessive emotional damage when losing
* You may start judging your own face differently
* Game may become *too personal*

---

## 🚀 Running the Game

```bash
python main.py
```

Make sure:

* Your assets are in the correct folders
* DIPPID is running and sending sensor data
* You are holding your phone **sideways** (yes, again, this matters)

---

## 🧠 Final Advice

This game is not about winning.
It’s about survival… and self-reflection.

Good luck.