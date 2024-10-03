import pygame as pg, sys
import random
import os

# プレイヤー名の入力
player_name = input("プレイヤー名を入力してください: ")

# ファイルの存在確認用関数
def load_image(file_path, size=None):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} が見つかりません。")
        pg.quit()
        sys.exit()
    img = pg.image.load(file_path)
    if size:
        img = pg.transform.scale(img, size)
    return img

def load_sound(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} が見つかりません。")
        pg.quit()
        sys.exit()
    return pg.mixer.Sound(file_path)

# 初期化
pg.init()
screen = pg.display.set_mode((886, 600))

# 自機データ
myimg = load_image("images/myship.png", (50, 50))
myrect = pg.Rect(400, 500, 50, 50)

# ボスデータ
boss_img = load_image("images/Boss.png", (100, 100))
boss_rect = pg.Rect(393, -100, 100, 100)  # 初期位置は画面外上
boss_health = 40  # ボスの体力
boss_bullets = []  # ボスの弾を管理するリスト
boss_active = False  # ボスが出現しているかどうかのフラグ


# 弾データ
bulletimg = load_image("images/bullet.png", (16, 16))
bulletrect = pg.Rect(400, -100, 16, 16)

# UFOデータ
ufoimg = load_image("images/UFO.png", (50, 50))
ufos = [pg.Rect(random.randint(0, 800), -100 * i, 50, 50) for i in range(10)]
enemy_attack_power = 1  # 敵の攻撃力

# 星データ
starimg = load_image("./images/star.png", (12, 12))
stars = [pg.Rect(random.randint(0, 800), random.randint(-600, 0), 30, 30) for _ in range(60)]

# ボタンデータ
replay_img = load_image("images/replaybtn.png")

# サウンドデータの読み込み
pi_sound = load_sound("sounds/pi.wav")
down_sound = load_sound("sounds/down.wav")
piko_sound = load_sound("sounds/piko.wav")

# BGMデータの読み込み
bgm_sound = load_sound("sounds/bgm.wav")  # BGMファイルのパスを指定

# メインループの開始前にBGMを再生
bgm_sound.set_volume(0.3)  # 0.0~1.0の範囲で音量を調整
bgm_sound.play(loops=-1)  # ループ再生

# メインループで使う変数
pushFlag = False
page = 1
score = 0
enemy_strength = 1  # 敵の強さ
enemy_shoot = False  # 敵が弾を撃つかどうか
last_score_time = pg.time.get_ticks()  # スコア加算のタイマー
enemy_bullets = []  # 敵の弾のリスト

# ボタンを押したらページをジャンプする関数
def button_to_jump(btn, newpage):
    global page, pushFlag
    mdown = pg.mouse.get_pressed()
    (mx, my) = pg.mouse.get_pos()
    if mdown[0]:
        pi_sound.play()
        if btn.collidepoint(mx, my) and not pushFlag:
            page = newpage
            pushFlag = True
            return True  # ボタンが押されたことを返す
    else:
        pushFlag = False
    return False  # ボタンが押されていない場合はFalseを返す

# ゲームステージ
def gamestage():
    global score, page, enemy_strength, enemy_shoot, enemy_bullets, last_score_time
    screen.fill(pg.Color("NAVY"))

    # ユーザーからの入力を調べる
    (mx, my) = pg.mouse.get_pos()
    mdown = pg.mouse.get_pressed()

    # 星の処理
    for star in stars:
        star.y += star.w
        screen.blit(starimg, star)
        if star.y > 600:
            star.x = random.randint(0, 800)
            star.y = random.randint(-30, 0)

    # 自機の処理
    myrect.x = mx - 25
    screen.blit(myimg, myrect)

    # 弾の処理
    if mdown[0] and bulletrect.y < 0:
        bulletrect.x = myrect.x + 17
        bulletrect.y = myrect.y
        pi_sound.play()
    if bulletrect.y >= 0:
        bulletrect.y -= 15
        screen.blit(bulletimg, bulletrect)

    # UFOの処理
    for ufo in ufos:
        ufo.y += 2 + enemy_strength // 10  # 敵の移動速度を減少
        screen.blit(ufoimg, ufo)
        if ufo.y > 600:
            ufo.x = random.randint(0, 800)
            ufo.y = random.randint(-100, -50)

        # 自機とUFOの衝突処理
        if ufo.colliderect(myrect):
            page = 2
            down_sound.play()

        # 弾とUFOの衝突処理
        if ufo.colliderect(bulletrect):
            score += 1  # 敵を倒すと1ポイント加算
            ufo.y = random.randint(-100, -50)
            ufo.x = random.randint(0, 800)
            bulletrect.y = -100
            piko_sound.play()

        # 敵の弾を撃つ処理
        if enemy_shoot and random.randint(1, 100) < 2:  # 確率で弾を撃つ
            bullet_x = ufo.x + 17  # UFOの中央から弾を発射
            bullet_y = ufo.y + 50   # UFOの下から発射
            enemy_bullets.append(pg.Rect(bullet_x, bullet_y, 10, 10))

    # 敵の弾の処理
    for bullet in enemy_bullets:
        bullet.y += 8  # 弾の移動速度を上げる
        pg.draw.rect(screen, pg.Color("RED"), bullet)  # 赤色の弾を描画
        if bullet.y > 600:
            enemy_bullets.remove(bullet)  # 画面外に出た弾を削除

        # 自機と敵の弾の衝突処理
        if bullet.colliderect(myrect):
            page = 2
            down_sound.play()
    
    # スコアの処理
    current_time = pg.time.get_ticks()
    if current_time - last_score_time >= 1000:  # 1秒ごとにスコアを増加
        score += 1
        last_score_time = current_time

    # スコアに応じて敵を強化
    if score in [30, 60, 90]:
        enemy_strength += 1  # 敵の強さを増加
        enemy_shoot = True  # 敵が弾を撃つフラグを立てる

    # スコアが200を超えたらクリア画面に遷移
    if score >= 200:
        page = 3

    font = pg.font.Font(None, 48)
    text = font.render("SCORE: " + str(score), True, pg.Color("WHITE"))
    screen.blit(text, (20, 20))

# ゲームクリア画面を表示する関数
def congratulations():
    screen.fill(pg.Color("NAVY"))
    
    # 背景画像の表示
    congrats_img = load_image("images/Congratulations.png", (886, 600))
    screen.blit(congrats_img, (0, 0))  # 背景画像を表示
    
    # "ゲームクリア" テキストを中央に表示
    font = pg.font.Font(None, 150)
    text = font.render("GAMECLEAR", True, pg.Color("YELLOW"))
    text_rect = text.get_rect(center=(443, 200))  # 画面の中央上に配置
    screen.blit(text, text_rect)

     # 「音楽：魔王魂」を画面の一番下に表示
    font_small = pg.font.Font(None, 40)
    music_text = font_small.render("bgm:maoudamsii", True, pg.Color("WHITE"))

    # テキストを画面下部に表示 (画面の幅に合わせて中央揃え)
    screen.blit(music_text, (screen.get_width() // 2 - music_text.get_width() // 2, screen.get_height() - music_text.get_height() - 20))


     # リプレイボタンの配置を調整 (GAMEOVERの5mm下に配置)
    btn1 = screen.blit(replay_img, (320, text_rect.bottom + 14))  # 14ピクセル下に配置
    
    # ボタンが押されたらリセット
    if button_to_jump(btn1, 1):  # ボタンが押されたらページ1（ゲームスタート）に戻る
        gamereset()  # ゲームの状態をリセット

# データのリセット
def gamereset():
    global score, enemy_strength, enemy_shoot, enemy_bullets, last_score_time, ufos
    score = 0  # スコアをリセット
    enemy_strength = 1
    enemy_shoot = False
    enemy_bullets.clear()  # 敵の弾をリセット
    myrect.x = 400
    myrect.y = 500
    bulletrect.y = -100
    last_score_time = pg.time.get_ticks()  # スコア加算のタイマーをリセット
    for i in range(10):
        ufos[i] = pg.Rect(random.randint(0, 800), -100 * i, 50, 50)  # UFOの位置をリセット

# ゲームオーバー
def gameover():
    screen.fill(pg.Color("NAVY"))
    
    # GAMEOVERのテキスト表示
    font = pg.font.Font(None, 150)
    text = font.render("GAMEOVER", True, pg.Color("RED"))
    text_rect = text.get_rect(center=(443, 200))  # 画面の中央上に配置
    screen.blit(text, text_rect)

     # 「音楽：魔王魂」を画面の一番下に表示
    font_small = pg.font.Font(None, 40)
    music_text = font_small.render("bgm:maoudamsii", True, pg.Color("WHITE"))

    # テキストを画面下部に表示 (画面の幅に合わせて中央揃え)
    screen.blit(music_text, (screen.get_width() // 2 - music_text.get_width() // 2, screen.get_height() - music_text.get_height() - 20))
    
    # リプレイボタンの配置を調整 (GAMEOVERの5mm下に配置)
    btn1 = screen.blit(replay_img, (320, text_rect.bottom + 14))  # 14ピクセル下に配置
    
    # スコア表示
    font = pg.font.Font(None, 40)
    score_text = font.render("SCORE: " + str(score), True, pg.Color("WHITE"))
    screen.blit(score_text, (20, 20))
    
    # ボタンが押されたかをチェック
    if button_to_jump(btn1, 1):  # ボタンが押されたら
        gamereset()  # ゲームの状態をリセット

# メインループ
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

    # ページごとに処理を切り替え
    if page == 1:
        gamestage()  # ゲーム中
    elif page == 2:
        gameover()  # ゲームオーバー画面
    elif page == 3:
        congratulations()  # ゲームクリア画面

    # 画面を更新
    pg.display.update()
    pg.time.Clock().tick(60)