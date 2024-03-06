import pygame
import sys
import random


SIZE = WIDTH, HEIGHT = 600, 600


# 生命值
class HpSys:
    def __init__(self, card_sys: "CardSys") -> None:
        self._card_sys = card_sys
        # 生命值
        self.hp = 3
        # 生命值图像
        self.images: list[pygame.Surface] = [
            pygame.image.load(r"img/hp.png").convert_alpha()
            for _ in range(self.hp)
        ]
        # 开始失去生命的时间
        self.begin_lose_hp_time = None
        # 完全失去生命要花的时间
        self.lose_hp_COOL = 500
        self.losing_hp = False

    def begin_lose_hp(self):
        if self.losing_hp:
            return
        self.losing_hp = True
        self.begin_lose_hp_time = pygame.time.get_ticks()


    def update(self) -> None:
        if not self.losing_hp:
            return
        alpha = 255 * (self.lose_hp_COOL - pygame.time.get_ticks() + self.begin_lose_hp_time) / self.lose_hp_COOL
        self.images[-1].set_alpha(alpha)
        if alpha <= 0:
            self.losing_hp = False
            self._card_sys.free_checked_card()
            self.images.pop(-1)
            self.hp -= 1
            if self.hp <= 0:
                pygame.event.post(pygame.event.Event(pygame.QUIT))


    def draw(self, surface: pygame.Surface) -> None:
        for i, hp_image in enumerate(self.images):
            surface.blit(hp_image, (5 + i * (hp_image.get_width() + 5), 5))


# 卡牌
class Card(pygame.sprite.Sprite):
    def __init__(self, sys: "CardSys", id: int, topleft_pos: tuple[float, float]) -> None:
        super().__init__(sys)
        self._sys = sys
        # 卡片的身份
        self.id = id
        # 正面图像
        self.front_image: pygame.Surface = self._sys.images[self.id]
        #  背面图像
        self.back_image: pygame.Surface = pygame.image.load(r"img/back.png").convert_alpha()
        # 点击判定
        self.rect: pygame.Rect = self.front_image.get_rect(topleft=topleft_pos)
        # image
        self.image = self.front_image
        # 消失
        self.disappear = False
        # 开始消失时间
        self.begin_disappear_time = None
        # 完全消失要花的时间
        self.disappear_COOL = 500

        
    def be_click(self):
        self.image = self.front_image

    
    def update(self) -> None:
        if not self.disappear:
            return
        alpha = 255 * (self.disappear_COOL - pygame.time.get_ticks() + self.begin_disappear_time) / self.disappear_COOL
        self.image.set_alpha(alpha)
        if alpha <= 0:
            self.kill()
        
        
        
    def begin_disappear(self):
        if self.disappear:
            return
        self.disappear = True
        self.begin_disappear_time = pygame.time.get_ticks()
        self.image = self.image.copy()
        

# 卡牌管理系统  
class CardSys(pygame.sprite.Group):
    def __init__(self) -> None:
        super().__init__()
        # 被翻上来的卡牌
        self.clicked_sprites: pygame.sprite.Group[Card] = pygame.sprite.Group()
        # 是不是在展示
        self.is_showing = True
        # 展示时间
        self.display_COOL = 3 * 1000
        # 开始展示的时间
        self.begin_display_time = pygame.time.get_ticks()
        # 载入图像
        self._load_imgae()
        # 载入卡牌
        self.fill_card()
        # hp
        self.hp_sys = HpSys(self)
    

    def handle_click(self, click_pos: tuple[int, int]):
        if self.is_showing or len(self.clicked_sprites) >= 2:
            return
        card: Card
        for card in self:
            if card.rect.collidepoint(click_pos):
                card.be_click()
                self.clicked_sprites.add(card)


    def handle_clicked_card(self):
        # 处理被翻过的牌
        a, b, *_ = self.clicked_sprites
        if a.id == b.id:
            a.begin_disappear()
            b.begin_disappear()
        else:
            self.hp_sys.begin_lose_hp()


    def fill_card(self) -> None:
        id_list: list[int] = [0,0,1,1,2,2]
        random.shuffle(id_list)
        image_width, image_height = self.images[0].get_size()
        left = (WIDTH - 3 * image_width - 2 * 40) / 2
        top = (HEIGHT - 2 * image_height - 40) / 2
        for i, id in enumerate(id_list):
            self.add(
                Card(
                    self,
                    id,
                    (
                        left + i % 3 * (image_width + 40),
                        top + i // 3 * (image_height + 40)
                    )
                )
            )

    def _load_imgae(self):
        # 图像
        self.images: list[pygame.Surface] = [
            pygame.image.load(r"img/font.png").convert_alpha()
            for _ in range(3)
        ]
        # 加载图像
        rect = pygame.Rect(
            self.images[0].get_width() / 2 - 15,
            self.images[0].get_height() / 2 - 15,
            30,
            30
        )
        x, y = rect.center
        pygame.draw.rect(self.images[0], "#ED1C24", rect)
        pygame.draw.circle(self.images[1], "#22B14C", (x, y), 15)
        pygame.draw.polygon(
            self.images[2],
            "#3F48CC",
            [(x, y - 15), (x + 15, y), (x, y + 15), (x - 15, y)]
        )


    def update(self) -> None:
        if self.is_showing:
            if pygame.time.get_ticks() - self.begin_display_time >= self.display_COOL:
                self.is_showing = False
                self.colse_card()
        elif len(self.clicked_sprites) >= 2:
            self.handle_clicked_card()
        self.hp_sys.update()
        if not self:
            self.re_start()
        return super().update()
    

    def colse_card(self) -> None:
        card: Card
        for card in self:
            card.image = card.back_image


    def draw(self, surface: pygame.Surface):
        self.hp_sys.draw(surface)
        if self.is_showing:
            rect = (
                50,
                HEIGHT - 50,
                (WIDTH - 100) * (self.display_COOL - pygame.time.get_ticks() + self.begin_display_time) / self.display_COOL, 
                25
            )
            border_rect = (50, HEIGHT - 50, WIDTH - 100, 25)
            pygame.draw.rect(surface, "#00A2E8", rect)
            pygame.draw.rect(surface, "#000000", border_rect, 4)
        return super().draw(surface)
    

    def free_checked_card(self):
        card: Card
        for card in self.clicked_sprites:
            card.image = card.back_image
        self.clicked_sprites.empty()


    def re_start(self):
        self.fill_card()
        self.is_showing = True
        self.begin_display_time = pygame.time.get_ticks()


# 基础game组件
class Windows:
    def __init__(self) -> None:
        pygame.init()
        self.surface = pygame.display.set_mode(SIZE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("卡牌匹配")
        self.quit = False


    def control(self):
        ...


    def update(self):
        ...


    def draw(self):
        pygame.display.flip()


    def run(self):
        while not self.quit:
            self.control()
            self.update()
            self.draw()
            self.clock.tick(60)
        self.safe_quit()


    def safe_quit(self):
        pygame.quit()
        sys.exit()

# 游戏
class Game(Windows):
    def __init__(self) -> None:
        super().__init__()
        # 卡牌系统
        self.card_sys = CardSys()

    
    def control(self):
        event: pygame.event.Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
                continue
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.card_sys.handle_click(event.pos)


    def update(self):
        self.card_sys.update()
        return super().update()
    

    def draw(self):
        self.surface.fill("#F5BD53")
        self.card_sys.draw(self.surface)
        return super().draw()


Game().run()
