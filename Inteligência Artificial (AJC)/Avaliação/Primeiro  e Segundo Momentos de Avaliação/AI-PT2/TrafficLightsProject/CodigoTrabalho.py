from src.images_location import *  # Importa as localizações de imagens

import random
import time
import threading
import pygame
import sys
import os
import logging
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template
from spade.message import Message
import asyncio
import spade

# Configuração do caminho do arquivo de log
log_file_path = "C:\\Users\\Rafael\\Desktop\\AI-PT2\\AI-PT2\\logs.txt"

# Garante a existência da pasta do arquivo de log
log_dir = os.path.dirname(log_file_path)
os.makedirs(log_dir, exist_ok=True)

# Configuração do logger, com um caminho específico
logging.basicConfig(filename=log_file_path, level=logging.INFO,
                    format='%(asctime)s [%(levelname)s]: %(message)s')

# Mensagem de log indicando que os semáforos estão ligados
logging.info("Sistema de semáforos inteligentes ativado.")

# Valores padrão dos temporizadores dos sinais
defaultGreen = {0: 10, 1: 10, 2: 10, 3: 10}
defaultRed = 150
defaultYellow = 3

Semaforos = []
noOfSemaforos = 4
currentGreen = 0   # Indica qual sinal está verde no momento
nextGreen = (currentGreen + 1) % noOfSemaforos    # Indica qual sinal ficará verde em seguida
currentYellow = 0   # Indica se o sinal amarelo está ligado ou desligado

speeds = {'car': 4}  # Velocidades médias dos veículos

# Posição inicial [X, Y, coordenada do eixo X]
x = {'left': [0, 0, 1400], 'up': [1400, 1400, 700], 'right': [1400, 1400, 0], 'down': [602, 627, 595]}
# Posições dos carros na horizontal [Y, Y, coordenada Y]
y = {'left': [498, 370, 340], 'up': [348, 466, 800], 'right': [348, 466, 445], 'down': [800, 0, 0]}

mid = {'right': {'x': 630, 'y': 445}, 'down': {'x': 390, 'y': 390}, 'left': {'x': 750, 'y': 465},
       'up': {'x': 500, 'y': 475}}  # define o tempo verde do sinal aqui

# Define os veículos {'direita': {0: [], 1: [], 2: [], 'cruzados': 0}, 'baixo': {0: [], 1: [], 2: [], 'cruzados': 0}, 'esquerda': {0: [], 1: [], 2: [], 'cruzados': 0}, 'cima': {0: [], 1: [], 2: [], 'cruzados': 0}}
vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}
vehicleTypes = {0: 'car', 1: 'ambu'}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Coordenadas da imagem do sinal, temporizador e contagem de veículos
# Cordenada do sinal superior esquerdo, sinal superior direito, sinal inferior direito, sinal inferior esquerdo
signalCoods = [(530, 570), (530, 230), (810, 230), (810, 570)]
signalTimerCoods = [(530, 550), (530, 210), (810, 210), (810, 550)]

# Coordenadas das linhas de parada
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 490, 'down': 240, 'left': 910, 'up': 630}

# Espaço entre veículos
stoppingGap = 30    # Espaço de parada -5
movingGap = -10   # Espaço de movimento -18

# Define os tipos de veículos permitidos aqui
allowedVehicleTypes = {'car': True}
allowedVehicleTypesList = []
vehiclesTurned = {'right': {1: [], 2: []}, 'down': {1: [], 2: []}, 'left': {1: [], 2: []}, 'up': {1: [], 2: []}}
vehiclesNotTurned = {'right': {1: [], 2: []}, 'down': {1: [], 2: []}, 'left': {1: [], 2: []}, 'up': {1: [], 2: []}}
rotationAngle = 3
# mid = {'right': {'x':645, 'y':445}, 'down': {'x':695, 'y':398}, 'left': {'x':1000, 'y':465}, 'up': {'x':695, 'y':550}}# define o tempo verde aleatório do sinal aqui
randomGreenSignalTimer = True
# define o intervalo aleatório do tempo verde do sinal aqui
randomGreenSignalTimerRange = [8, 13]

timeElapsed = 0
simulationTime = 300
timeElapsedCoods = (1100, 50)
vehicleCountTexts = ["0", "0", "0", "0"]
# Cordenada Superior Direita, Inferior Direita, Inferior Esquerda, Inferior Direita
vehicleCountCoods = [(480, 550), (480, 210), (880, 210), (880, 550)]

pygame.init()
simulation = pygame.sprite.Group()

class SemaforoTransito:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        self.crossedIndex = 0

        path = car_path + direction + "\\" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.image = pygame.image.load(path)

        if(len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0):
            if(direction == 'right'):
                self.stop = vehicles[direction][lane][self.index - 1].stop \
                            - vehicles[direction][lane][self.index - 1].image.get_rect().width \
                            - stoppingGap
            elif(direction == 'left'):
                self.stop = vehicles[direction][lane][self.index - 1].stop \
                            + vehicles[direction][lane][self.index - 1].image.get_rect().width \
                            + stoppingGap
            elif(direction == 'down'):
                self.stop = vehicles[direction][lane][self.index - 1].stop \
                            - vehicles[direction][lane][self.index - 1].image.get_rect().height \
                            - stoppingGap
            elif(direction == 'up'):
                self.stop = vehicles[direction][lane][self.index - 1].stop \
                            + vehicles[direction][lane][self.index - 1].image.get_rect().height \
                            + stoppingGap
        else:
            self.stop = defaultStop[direction]

        # Define a nova coordenada de início e parada
        if(direction == 'right'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] -= temp
        elif(direction == 'left'):
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif(direction == 'down'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif(direction == 'up'):
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)


    def render(self, screen):
        # Renderiza a imagem do veículo na tela nas coordenadas (self.x, self.y)
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        # Move o veículo com base na direção
        if self.direction == 'right':
            # Verifica se o veículo cruzou a linha de parada
            if self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                # Verifica se o veículo deve virar à direita
                if self.willTurn == 0:
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1

            if self.willTurn == 1:
                # Lógica para veículos que viram à direita
                if self.lane == 1:
                    # Verificações para garantir que o veículo siga as regras de virada à direita
                    if (self.crossed == 0 or self.x + self.image.get_rect().width < stopLines[self.direction] + 40):
                        if ((self.x + self.image.get_rect().width <= self.stop or
                             (currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and
                                (self.index == 0 or self.x + self.image.get_rect().width <
                                 (vehicles[self.direction][self.lane][self.index - 1].x - movingGap) or
                                 vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.x += self.speed
                    else:
                        if self.turned == 0:
                            # Lógica para girar o veículo à direita
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x += 2.4
                            self.y -= 2.8
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            # Movimenta o veículo após a virada à direita
                            if self.crossedIndex == 0 or (
                                    self.y > (vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y +
                                              vehiclesTurned[self.direction][self.lane][
                                                  self.crossedIndex - 1].image.get_rect().height + movingGap)):
                                self.y -= self.speed
                elif(self.lane == 2):
                    # Lógica para a terceira faixa de veículos
                    if(self.crossed==0 or self.x+self.image.get_rect().width<mid[self.direction]['x']):
                        # Verifica se o veículo cruzou a linha de parada ou está antes do meio
                        if((self.x+self.image.get_rect().width<=self.stop or (currentGreen==0 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.x+self.image.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                 
                            self.x += self.speed
                    else:
                        if(self.turned==0):
                            # Lógica para girar o veículo à esquerda
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x += 2
                            self.y += 1.8
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            # Movimenta o veículo após a virada à esquerda
                            if(self.crossedIndex==0 or ((self.y+self.image.get_rect().height)<(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].y - movingGap))):
                                self.y += self.speed
            else: 
                # Lógica para veículos em faixas não específicas
                if(self.crossed == 0):
                    # Verifica se o veículo cruzou a linha de parada
                    if((self.x+self.image.get_rect().width<=self.stop or (currentGreen==0 and currentYellow==0)) and (self.index==0 or self.x+self.image.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - movingGap))):                
                        self.x += self.speed
                else:
                    # Movimenta o veículo após cruzar a linha de parada
                    if((self.crossedIndex==0) or (self.x+self.image.get_rect().width<(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].x - movingGap))):                 
                        self.x += self.speed
        elif(self.direction=='down'):
            # Lógica para a direção 'down'
            if(self.crossed==0 and self.y+self.image.get_rect().height>stopLines[self.direction]):
                # Verifica se o veículo cruzou a linha de parada
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                # Verifica se o veículo deve virar à direita
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                # Verifica se o veículo deve virar
                if(self.lane == 1):
                    # Lógica para a primeira faixa ao virar
                    if(self.crossed==0 or self.y+self.image.get_rect().height<stopLines[self.direction]+50):
                        # Verifica se o veículo cruzou a linha de parada ou está antes da linha de virada
                        if((self.y+self.image.get_rect().height<=self.stop or (currentGreen==1 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.y+self.image.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                            self.y += self.speed
                    else:
                        # Lógica para veículos que não estão na primeira faixa ao virar   
                        if(self.turned==0):
                            # Lógica para girar o veículo à esquerda
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x += 1.2
                            self.y += 1.8
                            if(self.rotateAngle==90):
                                # Verifica se o veículo completou a virada
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            # Lógica para veículos que não estão na primeira faixa ao virar à esquerda
                            if(self.crossedIndex==0 or ((self.x + self.image.get_rect().width) < (vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].x - movingGap))):
                                # Verifica se o veículo cruzou a linha de parada ou está antes do veículo virado anteriormente
                                self.x += self.speed
                # Lógica para veículos na segunda faixa                
                elif(self.lane == 2):
                    # Verifica se o veículo cruzou a linha de parada ou está antes do meio
                    if(self.crossed==0 or self.y+self.image.get_rect().height<mid[self.direction]['y']):
                        # Verifica se o veículo cruzou a linha de parada ou está antes da linha de virada
                        if((self.y+self.image.get_rect().height<=self.stop or (currentGreen==1 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.y+self.image.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                            self.y += self.speed
                    else:
                        # Lógica para veículos que não estão na primeira faixa ao virar à direita   
                        if(self.turned==0):
                            # Lógica para girar o veículo à direita
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x -= 2.5
                            self.y += 2
                            if(self.rotateAngle==90):
                                # Verifica se o veículo completou a virada
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            # Movimenta o veículo após a virada à direita
                            if(self.crossedIndex==0 or (self.x>(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].x + vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().width + movingGap))): 
                                self.x -= self.speed
            else:
                # Lógica para veículos que não estão na primeira faixa ao virar 
                if(self.crossed == 0):
                    # Verifica se o veículo cruzou a linha de parada
                    if((self.y+self.image.get_rect().height<=self.stop or (currentGreen==1 and currentYellow==0)) and (self.index==0 or self.y+self.image.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - movingGap))):                
                        self.y += self.speed
                else:
                    # Movimenta o veículo após cruzar a linha de parada
                    if((self.crossedIndex==0) or (self.y+self.image.get_rect().height<(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].y - movingGap))):                
                        self.y += self.speed
        elif(self.direction=='left'):
            # Lógica para a direção 'left'
            if(self.crossed==0 and self.x<stopLines[self.direction]):
                # Verifica se o veículo cruzou a linha de parada
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                # Verifica se o veículo deve virar à esquerda
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                # Lógica para veículos que viram à esquerda
                if(self.lane == 1):
                    # Verificações para garantir que o veículo siga as regras de virada à esquerda
                    if(self.crossed==0 or self.x>stopLines[self.direction]-70):
                        if((self.x>=self.stop or (currentGreen==2 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                            self.x -= self.speed
                    else: 
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x -= 1
                            self.y += 1.2
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or ((self.y + self.image.get_rect().height) <(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].y  -  movingGap))):
                                self.y += self.speed
                elif(self.lane == 2):
                    if(self.crossed==0 or self.x>mid[self.direction]['x']):
                        if((self.x>=self.stop or (currentGreen==2 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                            self.x -= self.speed
                    else:
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x -= 1.8
                            self.y -= 2.5
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or (self.y>(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].y + vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().height +  movingGap))):
                                self.y -= self.speed
            else: 
                if(self.crossed == 0):
                    if((self.x>=self.stop or (currentGreen==2 and currentYellow==0)) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap))):                
                        self.x -= self.speed
                else:
                    if((self.crossedIndex==0) or (self.x>(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].x + vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().width + movingGap))):                
                        self.x -= self.speed
        elif(self.direction=='up'):
            if(self.crossed==0 and self.y<stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.lane == 1):
                    if(self.crossed==0 or self.y>stopLines[self.direction]-60):
                        if((self.y>=self.stop or (currentGreen==3 and currentYellow==0) or self.crossed == 1) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height +  movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):
                            self.y -= self.speed
                    else:   
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x -= 2
                            self.y -= 1.2
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or (self.x>(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].x + vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().width + movingGap))):
                                self.x -= self.speed
                elif(self.lane == 2):
                    if(self.crossed==0 or self.y>mid[self.direction]['y']):
                        if((self.y>=self.stop or (currentGreen==3 and currentYellow==0) or self.crossed == 1) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height +  movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):
                            self.y -= self.speed
                    else:   
                        if(self.turned==0):
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x += 1
                            self.y -= 1
                            if(self.rotateAngle==90):
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if(self.crossedIndex==0 or (self.x<(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].x - vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().width - movingGap))):
                                self.x += self.speed
            else: 
                if(self.crossed == 0):
                    if((self.y>=self.stop or (currentGreen==3 and currentYellow==0)) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height + movingGap))):                
                        self.y -= self.speed
                else:
                    if((self.crossedIndex==0) or (self.y>(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].y + vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().height + movingGap))):                
                        self.y -= self.speed 


class Environment:
    def __init__(self):
        # Inicializa variáveis do ambiente, como posições das aeronaves, condições climáticas, status das pistas, etc.
        self.aircraft_positions = {}  # Dicionário para armazenar as posições das aeronaves
        self.weather_conditions = {}  # Dicionário para armazenar as condições climáticas
        self.runway_status = {}  # Dicionário para armazenar o status das pistas


# Função que indica o início do funcionamento dos sinais com valores padrão
def initialize():
    # Define os valores mínimo e máximo para o temporizador de sinais verdes
    minTime = randomGreenSignalTimerRange[0]
    maxTime = randomGreenSignalTimerRange[1]

    if randomGreenSignalTimer:
        # Inicializa os sinais com tempos de semáforo verde aleatórios
        ts1 = SemaforoTransito(0, defaultYellow, random.randint(minTime, maxTime))
        Semaforos.append(ts1)
        ts2 = SemaforoTransito(ts1.red + ts1.yellow + ts1.green, defaultYellow, random.randint(minTime, maxTime))
        Semaforos.append(ts2)
        ts3 = SemaforoTransito(defaultRed, defaultYellow, random.randint(minTime, maxTime))
        Semaforos.append(ts3)
        ts4 = SemaforoTransito(defaultRed, defaultYellow, random.randint(minTime, maxTime))
        Semaforos.append(ts4)
    else:
        # Inicializa os sinais com tempos de semáforo verde padrão
        ts1 = SemaforoTransito(0, defaultYellow, defaultGreen[0])
        Semaforos.append(ts1)
        ts2 = SemaforoTransito(ts1.yellow + ts1.green, defaultYellow, defaultGreen[1])
        Semaforos.append(ts2)
        ts3 = SemaforoTransito(defaultRed, defaultYellow, defaultGreen[2])
        Semaforos.append(ts3)
        ts4 = SemaforoTransito(defaultRed, defaultYellow, defaultGreen[3])
        Semaforos.append(ts4)

    # Chama a função repeat para iniciar o ciclo do semáforo
    repeat()

    
# SemaforoAgent = agente do semáforo
class SemaforoAgent(Agent):
    def __init__(self, jid, password, environment):
        super().__init__(jid, password)
        self.environment = environment

    async def setup(self):
        # Define um comportamento para interagir com o ambiente e o controle de tráfego aéreo
        class SemaforoBehavior(CyclicBehaviour):
            async def run(self):
                # Perceber dados do ambiente
                aircraft_position = self.get_aircraft_position()

                # Atualizar posição da aeronave
                self.agent.environment.update_aircraft_position(100, 3000)

                # Comunicar com o controle de tráfego aéreo
                await self.send_instruction_to_atc(aircraft_position)

            def get_aircraft_position(self):
                # Acessar o objeto de ambiente para obter a posição da aeronave
                return self.agent.environment.get_aircraft_position()

            async def send_instruction_to_atc(self, position):
                # Criar uma mensagem ACL para enviar dados ao agente de controle de tráfego aéreo
                msg = Message(to="ambiente@localhost")  # Substituir pelo JID correto do agente de ATC
                msg.set_metadata("performative", "inform")
                msg.body = f"Aeronave na posição {position} solicitando instruções."

                # Enviar a mensagem
                await self.send(msg)

        # Adicionar o comportamento ao agente
        self.add_behaviour(SemaforoBehavior())



async def main():
    # Cria e inicializa o ambiente
    ambiente = Environment()

    # Inicializa os agentes semáforo
    Semaforo1 = SemaforoAgent("semaforo1@localhost", "1234", ambiente)
    print("Semaforo Inteligente 1 ativado")
    Semaforo2 = SemaforoAgent("semaforo2@localhost", "1234", ambiente)
    print("Semaforo Inteligente 2 ativado")
    Semaforo3 = SemaforoAgent("semaforo3@localhost", "1234", ambiente)
    print("Semaforo Inteligente 3 ativado")
    Semaforo4 = SemaforoAgent("semaforo4@localhost", "1234", ambiente)
    print("Semaforo Inteligente 4 ativado")
    Semaforo_group = SemaforoAgent("semaforosmuitoscarros@localhost", "1234", ambiente)

    # Inicia os agentes semáforo
    await Semaforo1.start(auto_register=True)
    await Semaforo2.start(auto_register=True)
    await Semaforo3.start(auto_register=True)
    await Semaforo4.start(auto_register=True)
    await Semaforo_group.start(auto_register=True)

    # Aguarda por um curto período de tempo
    await asyncio.sleep(1)



if __name__ == "__main__":
    spade.run(main())

#Função para verificar se há veículos atrás do  semáforo
def check_open_signal():
    ambiente = Environment()

    for i, (direction, semaforo_name) in enumerate(zip(directionNumbers.values(), ["semaforo1", "semaforo2", "semaforo3", "semaforo4"])):
        total_cars_behind_lines = 0

        for lane in range(3):
            for vehicle in vehicles[direction][lane]:
                if (direction == 'right' and vehicle.x < stopLines[direction]) or \
                   (direction == 'down' and vehicle.y < stopLines[direction]) or \
                   (direction == 'left' and vehicle.x > stopLines[direction]) or \
                   (direction == 'up' and vehicle.y > stopLines[direction]):
                    total_cars_behind_lines += 1
                    print(f"carro no {semaforo_name}!")

        # Mensagens de log para dar info de quando os semáforos funcionam normalmente, e warning quando a função muda
        if total_cars_behind_lines > 5:
            Semaforo_group = SemaforoAgent(f"{semaforo_name}@localhost", "1234", ambiente)
            Semaforo_group.start(auto_register=True)
            print(f"Trânsito intenso no {semaforo_name}! Mudem os sinais.")
            
            # Ajusta o temporizador do verde e vermelho apenas quando houver mais de 5 carros
            Semaforos[i].green += 5
            Semaforos[i].red += 5
        else:
            Semaforo_group = SemaforoAgent(f"{semaforo_name}p@localhost", "1234", ambiente)
            Semaforo_group.start(auto_register=True)
            print(f"Trânsito normal no {semaforo_name}.")

    return total_cars_behind_lines > 5
                                

def repeat():
    global currentGreen, currentYellow, nextGreen

    while Semaforos[currentGreen].green > 0:
        updateValues()
        time.sleep(1)
        if check_open_signal():
            Semaforos[currentGreen].green = 0  # Força o temporizador do verde para zero
        else:
            Semaforos[currentGreen].green -= 1  # Continue contando normalmente

    currentYellow = 1

    for i in range(0):  # Certifique-se de ajustar conforme necessário
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]

    while Semaforos[currentGreen].yellow > 0:  # Agora continua enquanto o amarelo não chegar a zero
        updateValues()
        time.sleep(1)

    currentYellow = 0

    Semaforos[currentGreen].green = defaultGreen[currentGreen]
    Semaforos[currentGreen].yellow = defaultYellow
    Semaforos[currentGreen].red = defaultRed

    currentGreen = nextGreen
    nextGreen = (currentGreen + 1) % noOfSemaforos
    Semaforos[nextGreen].red = Semaforos[currentGreen].yellow + Semaforos[currentGreen].green

    repeat()
    
# Função que procede a uma atualização de valores dos temporizadores a cada segundo
def updateValues():
    for i in range(0, noOfSemaforos):
        if(i==currentGreen):
            if(currentYellow==0):
                Semaforos[i].green-=1
            else:
                Semaforos[i].yellow-=1
        else:
            Semaforos[i].red-=1


# Generating vehicles in the simulation
def generateVehicles():
    while(True):
        vehicle_type = random.randint(0,0) #random.choice(allowedVehicleTypesList) # vehicle_type = random.randint(0,0) #0= car, 1=..., 2=..., 3=....
        lane_number = random.randint(2,2)
        will_turn = 0
        if(lane_number == 1):
            temp = random.randint(0,99)
            if(temp<40):
                will_turn = 1
        elif(lane_number == 2):
            temp = random.randint(0,99)
            if(temp<40):
                will_turn = 1
        temp = random.randint(0,99)
        direction_number = 0
        dist = [25,50,75,100]
        if(temp<dist[0]):
            direction_number = 0
        elif(temp<dist[1]):
            direction_number = 1
        elif(temp<dist[2]):
            direction_number = 2
        elif(temp<dist[3]):
            direction_number = 3
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], will_turn)
        time.sleep(2)

# Função que mostra as estatísticas da simulação
def showStats():
    totalVehicles = 0
    print('Direction-wise Vehicle Counts')
    for i in range(0,4):
        if(Semaforos[i]!=None):
            print('Direction',i+1,':',vehicles[directionNumbers[i]]['crossed'])
            totalVehicles += vehicles[directionNumbers[i]]['crossed']
    print('Total vehicles passed:',totalVehicles)
    print('Total time:',timeElapsed)

# Função para uma contagem regressiva do tempo de simulação
def simTime():
    global timeElapsed, simulationTime
    while(True):
        timeElapsed += 1
        time.sleep(1)
        if(timeElapsed==simulationTime):
            showStats()
            os._exit(1) 

class Main:
    global allowedVehicleTypesList
    i = 0
    for vehicleType in allowedVehicleTypes:
        if(allowedVehicleTypes[vehicleType]):
            allowedVehicleTypesList.append(i)
        i += 1
    thread1 = threading.Thread(name="initialization",target=initialize, args=())    # initialization
    thread1.daemon = True
    thread1.start()

    # Colours 
    black = (0, 0, 0) 
    white = (255, 255, 255)

    # Screensize 
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load(background_image)

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    # Loading signal images and font
    redSignal = pygame.image.load(red_ligh_image)
    yellowSignal = pygame.image.load(yellow_light_image)
    greenSignal = pygame.image.load(green_light_image)
    font = pygame.font.Font(None, 30)
    
    thread2 = threading.Thread(name="generateVehicles",target=generateVehicles, args=())    # Generating vehicles
    thread2.daemon = True
    thread2.start()

    thread3 = threading.Thread(name="simTime",target=simTime, args=()) 
    thread3.daemon = True
    thread3.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                showStats()
                sys.exit()

        screen.blit(background,(0,0))   # display background in simulation
        for i in range(0,noOfSemaforos):  # display signal and set timer according to current status: green, yello, or red
            if(i==currentGreen):
                if(currentYellow==1):
                    Semaforos[i].signalText = Semaforos[i].yellow
                    screen.blit(yellowSignal, signalCoods[i])
                else:
                    Semaforos[i].signalText = Semaforos[i].green
                    screen.blit(greenSignal, signalCoods[i])
            else:
                if(Semaforos[i].red<=10):
                    Semaforos[i].signalText = Semaforos[i].red
                else:
                    Semaforos[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])
        signalTexts = ["","","",""]

        # display signal timer
        for i in range(0,noOfSemaforos):  
            signalTexts[i] = font.render(str(Semaforos[i].signalText), True, white, black)
            screen.blit(signalTexts[i],signalTimerCoods[i])

        # display vehicle count
        for i in range(0,noOfSemaforos):
            displayText = vehicles[directionNumbers[i]]['crossed']
            vehicleCountTexts[i] = font.render(str(displayText), True, black, white)
            screen.blit(vehicleCountTexts[i],vehicleCountCoods[i])

        # display time elapsed
        timeElapsedText = font.render(("Time Elapsed: "+str(timeElapsed)), True, black, white)
        screen.blit(timeElapsedText,timeElapsedCoods)

        # display the vehicles
        # Exibição dos veículos
        for vehicle in simulation:  
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()
        pygame.display.update()


Main()