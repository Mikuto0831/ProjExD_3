import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5 # 爆弾の数
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy
        self.dire=(+5,0)

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
            self.dire = sum_mv
        screen.blit(self.img, self.rct)


class Beam:
    """
    こうかとんが放つビームに関するクラス
    """
    def __init__(self, bird:"Bird"):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん（Birdインスタンス）
        """
        self.vx, self.vy = bird.dire
        theta = math.atan2(-self.vy, self.vx)
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), math.degrees(theta), 1)
        self.rct = self.img.get_rect()
        self.rct.centery = bird.rct.centery + bird.rct.height*self.vy/5 
        self.rct.centerx = bird.rct.centerx + bird.rct.width*self.vx/5
        

    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        if check_bound(self.rct) == (True, True):
            self.rct.move_ip(self.vx, self.vy)
            screen.blit(self.img, self.rct) 

    def is_over_monitor(self) -> bool:
        """
        ビームが画面内にいるか判定します
        戻り値 bool : 画面内にいるとTrue
        """
        return check_bound(self.rct) == (True, True)


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

class Score:
    def __init__(self) -> None:
        """
        スコアを表示するための初期化を行う
        """
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.color = (0,0,255)
        self.score = 0
        self.img = self.fonto.render(f"スコア:{self.score}", 0, self.color)
        self.center = [100, HEIGHT-50]
    
    def update(self, screen: pg.Surface) -> None:
        """
        最新のスコアを表示する
        引数 screen：画面Surface
        """
        self.img = self.fonto.render(f"スコア:{self.score}", 0, self.color)
        screen.blit(self.img, self.center)

    def add(self)-> None:
        """
        スコアを1加算する
        """
        self.score += 1

class Explosion:
    """
    爆発エフェクトに関するクラス
    """
    def __init__(self,bomb:Bomb) -> None:
        """
        爆発画像Surfaceを生成する
        引数 bomb：爆発した爆弾インスタンス
        """
        self.imgs = [
            pg.image.load(f"fig/explosion.gif"),
            pg.transform.flip(pg.image.load(f"fig/explosion.gif"),True,True)
        ]
        self.center = bomb.rct.center
        self.life = 20
    
    def update(self,screen: pg.Surface)->None:
        """
        爆発エフェクトを表示させ、lifeを減らす
        引数 screen：画面Surface
        """
        self.life -= 1
        screen.blit(self.imgs[self.life//4%2],self.center)
    
    def is_live(self)->bool:
        """
        この爆発エフェクトのliveが生きているか判定します
        戻り値 bool : 生きていたらTrue
        """
        return self.life >= 0

class Timer:
    """
    ゲームのタイマーをset/表示する
    """
    def __init__(self,time:int) -> None:
        """
        引き数 time : 行う秒数
        """
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.color = (0,0,255)
        self.time = time
        self.one_second_cnt = 0  # 一秒を数える
        self.img = self.fonto.render(f"残り時間:{self.time}秒", 0, self.color)
        self.center = [WIDTH-200, HEIGHT-50]
    
    def update(self, screen: pg.Surface) -> None:
        """
        タイマーを表示させ、一秒をカウントし、タイムを減らす
        引数 screen：画面Surface
        """
        self.img = self.fonto.render(f"残り時間:{self.time}秒", 0, self.color)
        screen.blit(self.img, self.center)

        self.one_second_cnt += 1
        if self.one_second_cnt >= 50:
            self.time -=1
            self.one_second_cnt = 0
    
    def is_time_over(self) -> bool:
        """
        タイムオーバーしているか判定します
        戻り値 : bool
        """
        return self.time < 0

        
def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    beams = []
    effects = []
    score = Score()
    timer = Timer(10)
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # スペースキー押下でBeamクラスのインスタンス生成
                beams.append(Beam(bird))            
        screen.blit(bg_img, [0, 0])
        
        if timer.is_time_over():
            # タイムオーバーじの画面切り替え
            img_num = 8
            text = "Time Over"
            if not bombs:
                # 全ての爆弾を打ち落としている際の設定
                img_num = 6
                text = "GameClear"
            bird.change_img(img_num, screen)
            fonto = pg.font.Font(None, 80)
            txt = fonto.render(text, True, (255, 0, 0))
            screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
            pg.display.update()
            time.sleep(5)
            return
            
        # 爆弾とこうかとんの衝突判定
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                pg.display.update()
                time.sleep(5)
                return
        
        # ビームと爆弾の衝突判定
        for i,bomb in enumerate(bombs):
            for j,beam in enumerate(beams):
                if bomb is not None and beam is not None:
                    if beam.rct.colliderect(bomb.rct):  # ビームと爆弾が衝突したら
                        effects.append(Explosion(bomb))
                        beams[j], bombs[i] = None, None
                        bird.change_img(6, screen)
                        score.add()
                        pg.display.update() 
        
        # 各配列
        bombs = [bomb for bomb in bombs if bomb is not None]
        beams = [beam for beam in beams if beam is not None and beam.is_over_monitor()]
        effects = [eff for eff in effects if eff.is_live()]

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        for beam in beams:
            beam.update(screen) 
        for bomb in bombs:  
            bomb.update(screen)
        for eff in effects:
            eff.update(screen)
        score.update(screen)
        timer.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
