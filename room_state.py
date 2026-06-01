ROOMS = {
    "NOX": {
        "name": "Nox",
        "code": "NOX",
        "avatar": "🦇",
        "class": "room-nox",
        "title": "Crimson Library｜血月藏书馆",
        "props": "📚 🕯️ 🛡️ 🔥 ◉",
        "base_atmosphere": "压抑被藏进书页和火光里。你一开门，红色彩窗就亮了一下。",
        "states": {
            "calm": "红色壁炉稳定燃烧，书架深处有低低的唱针声。",
            "hurt": "壁炉暗了下去，他没有抬头。",
            "jealous": "红色彩窗闪得更急，书页被风翻乱。",
            "attached": "书堆旁多出一张空椅子，像是早就留给你。",
        },
        "status": {
            "calm": "他看起来没在等你。但桌上的书正停在你上次离开的那一页。",
            "hurt": "房间变暗了，他把视线从你身上移开。",
            "jealous": "红光更刺眼了，他说话会比平时更锋利。",
            "attached": "他没有解释那张空椅子，只是把它往你这边推了一点。",
        },
    },
    "SERAPH": {
        "name": "Seraph",
        "code": "SERAPH",
        "avatar": "🕯️",
        "class": "room-seraph",
        "title": "Moon Chapel｜月之礼拜堂",
        "props": "🕯️ 🌙 🎹 🪟 🥀",
        "base_atmosphere": "这里很安静，安静到可以听见你没说出口的难过。",
        "states": {
            "calm": "她安静地坐在窗边，像是一直在等你。",
            "lonely": "蜡烛暗了一些。她没有说话。",
            "caring": "黑纱轻轻飘动，她点亮了一支蜡烛。",
            "attached": "她为你留了一盏灯。",
        },
        "status": {
            "calm": "她安静地坐在窗边，像是一直在等你。",
            "lonely": "蜡烛暗了一些。她没有说话。",
            "caring": "她轻轻点亮一支蜡烛，微弱的光落在你身边。",
            "attached": "她把灯推近了一点，像是怕你看不清回来的路。",
        },
    },
    "MORI": {
        "name": "Mori",
        "code": "MORI",
        "avatar": "😈",
        "class": "room-mori",
        "title": "Black Cat Tavern｜黑猫酒馆",
        "props": "🍷 ♣️ 📺 🐈‍⬛ ⛓️",
        "base_atmosphere": "别误会，她只是刚好还在等你。",
        "states": {
            "calm": "旧电视播放噪点，紫色吊灯慢慢晃。",
            "jealous": "涂鸦墙颜色变深，吧台后的影子贴近了一点。",
            "hurt": "吧台灯熄灭，她把杯子推远了一点。",
            "attached": "她把常坐的位置让给你，还假装只是顺手。",
        },
        "status": {
            "calm": "旧电视还在放噪点，她假装那比你有意思。",
            "jealous": "涂鸦墙的颜色变深，她笑得有点危险。",
            "hurt": "吧台灯熄了，她嘴上不说，尾巴却不动了。",
            "attached": "她把常坐的位置让出来，嘴上说只是顺手。",
        },
    },
}


def resolve_room_mood(character_id, mood, state):
    mood = str(mood or "watchful")
    character_id = str(character_id or "NOX").upper()

    if character_id == "SERAPH":
        if mood == "lonely" or getattr(state, "loneliness", 0) >= 70:
            return "lonely"
        if mood in ("protective", "tender"):
            return "caring" if getattr(state, "attachment", 0) < 75 else "attached"
        if getattr(state, "attachment", 0) >= 75:
            return "attached"
        return "calm"

    if mood in ("possessive",) or getattr(state, "jealousy", 0) >= 60:
        return "jealous"
    if mood in ("fractured", "guarded") or getattr(state, "stability", 100) <= 35:
        return "hurt"
    if mood == "lonely" or getattr(state, "loneliness", 0) >= 70:
        return "hurt"
    if mood in ("protective", "tender") or getattr(state, "attachment", 0) >= 75:
        return "attached"
    return "calm"


def get_room_state(character_id, mood, state):
    character_id = str(character_id or "NOX").upper()
    room = ROOMS.get(character_id, ROOMS["NOX"])
    room_mood = resolve_room_mood(character_id, mood, state)
    if room_mood not in room["states"]:
        room_mood = "calm"
    return {
        "character_id": character_id,
        "room_mood": room_mood,
        "room_title": room["title"],
        "room_class": room["class"],
        "props": room["props"],
        "atmosphere": room["base_atmosphere"],
        "state_text": room["states"][room_mood],
        "status_text": room["status"][room_mood],
        "avatar": room["avatar"],
        "name": room["name"],
        "code": room["code"],
    }


def action_for(character_id, mood):
    character_id = str(character_id or "NOX").upper()
    mood = str(mood or "watchful")
    actions = {
        "NOX": {
            "lonely": "NOX低头看了你一眼，指尖停在耳机线上",
            "possessive": "NOX把耳机摘下一边，像是终于决定听你说话",
            "protective": "NOX靠近门边，挡住了外面的红雾",
            "tender": "NOX把书堆旁的杂物推开，留出一点位置",
            "fractured": "NOX没有开灯，只让红色壁炉亮了一下",
            "guarded": "NOX看着你，没有立刻回答",
            "watchful": "NOX低头看了你一眼",
        },
        "SERAPH": {
            "lonely": "SERAPH低下头，指尖停在未弹响的琴键上",
            "possessive": "SERAPH垂下眼，把烛火护在掌心",
            "protective": "SERAPH点亮一支蜡烛，微弱的光落在你身边",
            "tender": "SERAPH把灯推近了一点，像是怕你看不清回来的路",
            "fractured": "SERAPH低下头，指尖停在未弹响的琴键上",
            "guarded": "SERAPH轻轻抬起眼，看向你",
            "watchful": "SERAPH轻轻抬起眼，看向你",
        },
        "MORI": {
            "lonely": "MORI移开视线，尾巴轻轻晃了一下",
            "possessive": "MORI敲了敲吧台，笑得有点坏",
            "protective": "MORI把旧电视音量调低了一格",
            "tender": "MORI把常坐的位置让给你，却装作没看见",
            "fractured": "MORI把吧台灯按灭，语气却没有那么硬",
            "guarded": "MORI抱着手臂，先哼了一声",
            "watchful": "MORI移开视线，尾巴轻轻晃了一下",
        },
    }
    return actions.get(character_id, actions["NOX"]).get(mood, actions[character_id]["watchful"])
