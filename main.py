from pygame import *
from random import *
from config import *
import math

init()
font.init()

# VARIABLES DEL JUEGO
puntos = 0
vidas = 5
flechas = 100
nivel = 1
dragones_derrotados_nivel = 0

# FUENTE
font_1 = font.Font(FONT_FILE, 25)

# PANTALLA
pantalla = display.set_mode((WIDTH, HEIGHT))
display.set_caption(TITLE)

# CARGAR IMAGENES
background = transform.smoothscale(image.load(BACK_IMG), (WIDTH, HEIGHT))
player_img = transform.smoothscale(image.load(PLAYER_IMG), (90, 90))
flecha_img = transform.smoothscale(image.load(BULLET_IMG), (22, 8))

dragon1_img = transform.smoothscale(image.load(DRAGON1_IMG), (100, 100))
dragon2_img = transform.smoothscale(image.load(DRAGON2_IMG), (95, 95))
dragon3_img = transform.smoothscale(image.load(DRAGON3_IMG), (120, 120))

# CLASE PADRE
class GameSprite(sprite.Sprite):
    def __init__(self, imagen, x, y):
        super().__init__()
        self.image = imagen
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        pantalla.blit(self.image, (self.rect.x, self.rect.y))

# CLASE JUGADOR
class Player(GameSprite):
    def __init__(self, imagen, x, y):
        super().__init__(imagen, x, y)
        self.rect.center = (x, y)
    
    def update(self):
        keys = key.get_pressed()
        
        if keys[K_LEFT] and self.rect.x > 0:
            self.rect.x -= 5  
        if keys[K_RIGHT] and self.rect.x < WIDTH - self.rect.width:
            self.rect.x += 5
    
    def draw(self):
        pantalla.blit(self.image, (self.rect.x, self.rect.y))
        
# CLASE FLECHA
class Flecha(sprite.Sprite):
    def __init__(self, imagen, x, y, target_x, target_y):
        super().__init__()
        self.image = imagen
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        dx = target_x - x
        dy = target_y - y
        distancia = math.sqrt(dx**2 + dy**2)
        
        if distancia > 0:
            self.vx = (dx / distancia) * 15
            self.vy = (dy / distancia) * 15
        else:
            self.vx = 0
            self.vy = 0
        
        self.gravedad = 0.2
    
    def update(self):
        self.vy += self.gravedad
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # si se sale de la pantalla, se elimina (se pega revisar)
        if self.rect.y > HEIGHT or self.rect.x > WIDTH or self.rect.x < self.rect.w:
            self.kill()
    
    def reset(self):
        pantalla.blit(self.image, (self.rect.x, self.rect.y))

# CLASE DRAGÓN
class Dragon(sprite.Sprite):
    def __init__(self, imagen, x, y, nivel):
        super().__init__()
        self.image = imagen
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.nivel = nivel
        self.vx = choice([-(2 + nivel), 2 + nivel])
        self.vy = randint(-(1 + nivel), 1 + nivel)
        self.vida = nivel * 2
        self.vida_max = nivel * 2
        #self.barra_vida = Rect(self.rect.x, self.rect.y - 10, self.rect.w, 15)

    
    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        if self.rect.x < 0 or self.rect.x > WIDTH - self.rect.width:
            self.vx *= -1
        if self.rect.y < 0 or self.rect.y > HEIGHT - 100:
            self.vy *= -1
    
    def draw_dragon(self):
        pantalla.blit(self.image, (self.rect.x, self.rect.y))
        #draw.rect (pantalla, GREEN, (self.rect.x, self.rect.y - 10,barra_vida, 5))
        

    

player = Player(player_img, WIDTH // 2, HEIGHT - 50)

flechas_group = sprite.Group()   
dragones_group = sprite.Group()  

run = True
finish = False
tiempo_generacion = 0
clock = time.Clock()

# FUNCIONES
def mostrar_mira(pos):
    x, y = pos
    draw.circle(pantalla, RED, (x, y), 15, 2)
    draw.circle(pantalla, RED, (x, y), 5, 1)
    draw.line(pantalla, RED, (x - 25, y), (x - 18, y), 2)
    draw.line(pantalla, RED, (x + 18, y), (x + 25, y), 2)
    draw.line(pantalla, RED, (x, y - 25), (x, y - 18), 2)
    draw.line(pantalla, RED, (x, y + 18), (x, y + 25), 2)
    draw.circle(pantalla, WHITE, (x, y), 2)

def generar_dragon():
    if len(dragones_group) < (3 + nivel):
        x = randint(0, WIDTH - 70)
        y = randint(50, HEIGHT // 2 - 50)
        
        if nivel == 1:
            img = dragon1_img
        elif nivel == 2:
            img = dragon2_img
        else:
            img = dragon3_img
    
        dragones_group.add(Dragon(img, x, y, nivel))  

def subir_nivel():
    global nivel, flechas, dragones_derrotados_nivel
    nivel += 1
    flechas += 5
    dragones_derrotados_nivel = 0

def disparar_flecha(x, y, target_x, target_y):
    flechas_group.add(Flecha(flecha_img, x, y, target_x, target_y))  

# CICLO PRINCIPAL
while run:
    mouse_pos = mouse.get_pos()
    
    for e in event.get():
        if e.type == QUIT:
            run = False
        
        if e.type == KEYDOWN:
            if e.key == K_r:
                puntos = 0
                vidas = 5
                flechas = 30
                nivel = 1
                dragones_derrotados_nivel = 0
                dragones_group.empty()  # VACIAR GRUPO
                flechas_group.empty()   # VACIAR GRUPO
                finish = False
            
            if e.key == K_ESCAPE:
                run = False
            

            if e.key == K_d and not finish and flechas > 0: #centrar flecha desde player
                disparar_flecha(player.rect.centerx, player.rect.centery, mouse_pos[0], mouse_pos[1])
                flechas -= 1
        
        if e.type == MOUSEBUTTONDOWN and e.button == 1 and not finish and flechas > 0:
            disparar_flecha(player.rect.centerx, player.rect.centery, mouse_pos[0], mouse_pos[1])
            flechas -= 1
    
    if not finish:
        pantalla.blit(background, (0, 0))
        
        tiempo_generacion += 1
        if tiempo_generacion > 45:
            generar_dragon()
            tiempo_generacion = 0
        
        player.update()
        player.draw()
        
        
        flechas_group.update()     
        dragones_group.update()     
        
        for dragon in dragones_group:
            dragon.draw_dragon()
        

        flechas_group.draw(pantalla)
        
            
            # Colision flecha - dragon
        for flecha in flechas_group:
                dragon_golpeado = sprite.spritecollide(flecha, dragones_group, False)
                for dragon in dragon_golpeado:
                    dragon.vida -= 1
                    flecha.kill() 
                    
                    if dragon.vida <= 0:
                        puntos += 20 * dragon.nivel
                        dragones_derrotados_nivel += 1
                        dragon.kill()  
                        
                        if dragones_derrotados_nivel >= 5:
                            subir_nivel()

                
                # Colisión jugador - dragón
        for dragon in dragones_group:
            if sprite.collide_rect(player, dragon):
                vidas -= 1
                dragon.kill()
                if vidas <= 0:
                    finish = True
                pantalla.fill(RED)
                display.update()
                time.wait(200)
        
        # TEXTOS
        texto_puntos = font_1.render(f'PUNTOS: {puntos}', 1, WHITE)
        pantalla.blit(texto_puntos, (10, 10))
        
        texto_nivel = font_1.render(f'NIVEL: {nivel}', 1, WHITE)
        pantalla.blit(texto_nivel, (10, 50))
        
        texto_dragones = font_1.render(f'DRAGONES: {dragones_derrotados_nivel}/5', 1, WHITE)
        pantalla.blit(texto_dragones, (10, 90))
        
        texto_vidas = font_1.render(f'VIDAS: {vidas}', 1, GREEN)
        pantalla.blit(texto_vidas, (10, 130))
        
        texto_flechas = font_1.render(f'FLECHAS: {flechas}', 1, WHITE)
        pantalla.blit(texto_flechas, (10, 170))
        
        mostrar_mira(mouse_pos)
        
        instrucciones = font_1.render('Mouse: Apuntar | D/Click: Disparar | R: Reiniciar', 1, WHITE)
        pantalla.blit(instrucciones, (WIDTH//2 - 200, HEIGHT - 30))
    
    else:
        pantalla.fill(BLACK)
        if vidas <= 0:
            gameover_text = font_1.render('GAME OVER', 1, RED)
            pantalla.blit(gameover_text, (WIDTH//2 - 70, HEIGHT//2 - 50))
        else:
            win_text = font_1.render('VICTORIA', 1, YELLOW)
            pantalla.blit(win_text, (WIDTH//2 - 60, HEIGHT//2 - 50))
        
        puntos_final = font_1.render(f'PUNTUACION: {puntos}', 1, WHITE)
        pantalla.blit(puntos_final, (WIDTH//2 - 80, HEIGHT//2))
        
        reinicio_text = font_1.render('Presiona R para reiniciar', 1, WHITE)
        pantalla.blit(reinicio_text, (WIDTH//2 - 120, HEIGHT - 50))
    


    display.update()
    clock.tick(FPS)

quit()