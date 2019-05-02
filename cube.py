# -*- coding: utf-8 -*-

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Drawing(object):

	# ORiGin of the CUBE
	# ponto de origem de cada cubo
	org_cubes = [[0,0,0],[1,0,0],[2,0,0],
				 [0,1,0],[1,1,0],[2,1,0],
				 [0,2,0],[1,2,0],[2,2,0],
				 [0,0,1],[1,0,1],[2,0,1],
				 [0,1,1],[1,1,1],[2,1,1],
				 [0,2,1],[1,2,1],[2,2,1],
				 [0,0,2],[1,0,2],[2,0,2],
				 [0,1,2],[1,1,2],[2,1,2],
				 [0,2,2],[1,2,2],[2,2,2]]

	# CUBE ON MOVE
	# faz a relação de quais cubos serão 
	# transformados em cada uma das 9 rotações
	move_type = [[ 18, 19, 20, 21, 22, 23, 24, 25, 26 ],	# rotação 0 no eixo Z
			 	 [  9, 10, 11, 12, 13, 14, 15, 16, 17 ],	# rotação 1 no eixo Z
				 [  0,  1,  2,  3,  4,  5,  6,  7,  8 ],	# rotação 2 no eixo Z
			 	 [  2, 11, 20,  5, 14, 23,  8, 17, 26 ],	# rotação 3 no eixo X
			 	 [  1, 10, 19,  4, 13, 22,  7, 16, 25 ],	# rotação 4 no eixo X
			 	 [  0,  9, 18,  3, 12, 21,  6, 15, 24 ],	# rotação 5 no eixo X
			 	 [  6,  7,  8, 15, 16, 17, 24, 25, 26 ],	# rotação 6 no eixo Y
				 [  3,  4,  5, 12, 13, 14, 21, 22, 23 ],	# rotação 7 no eixo Y
				 [  0,  1,  2,  9, 10, 11, 18, 19, 20 ]]	# rotação 8 no eixo Y

	# Colors
	colors = [[1.0,1.0,0.0],	# Amarelo
			  [1.0,1.0,1.0],	# Branco
			  [0.0,0.0,1.0],	# Azul
			  [0.0,1.0,0.0],	# Verde
			  [1.0,0.0,0.0],	# Vermelho
			  [1.0,0.5,0.0],	# Laranja
			  [0.5,0.5,0.5]]	# Cinza

	front =  [[0,0,0],
			  [0,0,0],			# Amarelo para a frente do cubo
			  [0,0,0]]
	back = 	 [[1,1,1],
			  [1,1,1],			# Branco para a trás do cubo
			  [1,1,1]]
	left = 	 [[2,2,2],
			  [2,2,2],			# Azul para esquerda do cubo
			  [2,2,2]]
	right =  [[3,3,3],
			  [3,3,3],			# Verde para direita do cubo
			  [3,3,3]]
	bottom = [[4,4,4],
			  [4,4,4],			# Vermelho para o bottom do cubo
			  [4,4,4]]
	top = 	 [[5,5,5],
			  [5,5,5],			# Laranja para o topo do cubo
			  [5,5,5]]

	# buffer para os cubos que foram alterados, para que não ocorra
	# o redesenho deles junto dos cubos que não estão na rotação
	dont_draw = []

	# visão do mundo
	viewangle = -45 	# panorama
	tipangle = 25 		# inclinação
	pseudo_zoom = -8	# aproximação

	# rotação
	speed = 5 			# velocidade de rotação
	moves = [] 			# salva as rotações feitas: [nº da rotação, flag p/ rot. inversa, eixo]
	rotating = False 	# indica se a rotação terminou
	theta = 0			# angulo de rotação

	is_solving = False # bloqueia a aplicação enquanto o cubo estiver se resolvendo

	# define a posição do cubo em relacão aos eixos
	d = [-1.5, -1.5, -1.5] # centraliza ele no mundo

	# vars para motion do mouse
	beginx = 0		# marca o x da posição inicial do mouse
	beginy = 0		# marca o y da posição inicial do mouse
	moving = False	# indica se o mouse está em movimento
	step = 0.25		# valor de zoom para o mouse

	# iluminação
	light_diffuse = [1.0, 1.0, 1.0, 1.0] 	# cor da luz
	light_position = [3.0, 3.0, 4.0, 1.0]  	# posição da luz

	def __init__(self):
		
		glutInit()
		glutInitWindowSize(800, 600)
		glutInitWindowPosition(1000, 600)
		glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE)

		glutCreateWindow("Rubik's Cube")
		glutDisplayFunc(self.display)
		glutSpecialFunc(self.special_keys)
		glutKeyboardFunc(self.keyboard)
		glutMouseFunc(self.mouse)
		glutMotionFunc(self.motion)

		glClearColor(0.1, 0.0, 0.1, 1.0) # cor do fundo
		glMatrixMode(GL_PROJECTION)
		gluPerspective(60, 1.5, 0.1, 100) # angulo de visão em y, proporção da tela em x, zNear, zFar
		glMatrixMode(GL_MODELVIEW)
		glutMainLoop()

	# faz o tracking do cursor ao mesmo tempo que muda a visão do mundo
	def motion(self, x, y):
		if self.moving:
			self.viewangle = self.viewangle + (x - self.beginx)
			self.beginx = x
			self.tipangle = self.tipangle + (y - self.beginy)
			self.beginy = y
			glutPostRedisplay()

	# define o comportamento do mundo quando um evento do mouse ocorre
	def mouse(self, btn, state, x, y):
		# set o flag para ativar o motion do objeto a partir do mouse
		if btn == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
			self.moving = True
			self.beginx = x
			self.beginy = y

		# caso o botão de rolagem seja rolado, 
		# translada-se o mundo de modo a causar 
		# um efeito de zoom
		elif btn == 3 and self.pseudo_zoom <= -5.5:
			self.pseudo_zoom += self.step
		elif btn == 4 and self.pseudo_zoom >= -20:
			self.pseudo_zoom -= self.step

		glutPostRedisplay()

	# define como o OpenGL deve tratar as teclas especiais pressionadas
	def special_keys(self, key, x, y):
		
		# basicamente é definido que as teclas de seta alterar irão a
		# visão do mundo, isso é feito manipulando os valores de ângulo
		# e panorama definidos no ínicio da classe e usados no método 
		# display()

		if key == GLUT_KEY_LEFT:
			self.viewangle -= 5
		elif key == GLUT_KEY_RIGHT:
			self.viewangle += 5
		elif key == GLUT_KEY_UP:
			self.tipangle -= 5
		elif key == GLUT_KEY_DOWN:
			self.tipangle += 5

		glutPostRedisplay() # usado para atualizar a tela

	# define as ações de cada tecla normal pressionada
	def keyboard(self, key, x, y):
		action_keys = 'qawsedrftgyhujikol' # teclas aceitáveis
		
		# verifica se não está ocorrendo alguma rotação, se o cubo não 
		# está se resolvendo e se a key pressionada é válida
		if not self.rotating and not self.is_solving and key in action_keys: 
			
			if key == 'q':
				self.moves.append([0, False, 'z']) # [nº da rotação, se é inversa, e o eixo]
			
			elif key == 'a':
				self.moves.append([0, True, 'z'])
			
			elif key == 'w':
				self.moves.append([1, False, 'z'])

			elif key == 's':
				self.moves.append([1, True, 'z'])
			
			elif key == 'e':
				self.moves.append([2, False, 'z'])
			
			elif key == 'd':
				self.moves.append([2, True, 'z'])
			
			elif key == 'r':
				self.moves.append([3, True, 'x'])

			elif key == 'f':
				self.moves.append([3, False, 'x'])

			elif key == 't':
				self.moves.append([4, True, 'x'])

			elif key == 'g':
				self.moves.append([4, False, 'x'])

			elif key == 'y':
				self.moves.append([5, True, 'x'])

			elif key == 'h':
				self.moves.append([5, False, 'x'])

			elif key == 'u':
				self.moves.append([6, True, 'y'])

			elif key == 'j':
				self.moves.append([6, False, 'y'])

			elif key == 'i':
				self.moves.append([7, True, 'y'])

			elif key == 'k':
				self.moves.append([7, False, 'y'])

			elif key == 'o':
				self.moves.append([8, True, 'y'])

			elif key == 'l':
				self.moves.append([8, False, 'y'])

			self.rotating = True 				# marca o inicio da rotação
			glutIdleFunc(self.spin_cube)		# inicia a recursão

		# espaço é usado como tecla de ativação para a animação de
		# elucidação do cubo
		elif key == ' ' and not self.rotating and not self.is_solving: 
			glutIdleFunc(self.unravel) # inicia animação da solução

	# função para solucionar o cubo, ela funciona desfazendo todos os
	# movimentos feitos e removendos da lista até que não sobre nenhum
	def unravel(self):

		# a solução termina quando todos os movimentos foram desfeitos
		if not self.moves:
			self.is_solving = False	
			glutIdleFunc(None) # termina a recursão

		else:
			if not self.is_solving: # verifica se já não iniciou a solução para...
				self.is_solving = True
				for i in xrange(len(self.moves)):
					self.moves[i][1] = not self.moves[i][1] # ...evitar de negar duas vezes

			self.rotating = True 	# marca o inicio da rotação

			# Verifica se a rotação é inversa (true = inversa)
			self.theta += -10 if self.moves[-1][1] else 10

			if self.theta >= 90 or self.theta <= -90: # rotação completa em 90
				self.rotating = False
				self.theta = 0
				self.update_colors() 	# atualiza cores
				self.moves.pop() 		# remove os movimentos que foram desfeitos
			
			glutPostRedisplay() # atualiza a tela

	# essencial para a animação da rotação do cubo
	def spin_cube(self):

		# Verifica se a rotação é inversa (true = inversa) e adiciona o necessário 
		# ao ângulo da rotação
		self.theta += -(0.5 + self.speed) if self.moves[-1][1] else (0.5 + self.speed)

		if self.theta >= 90 or self.theta <= -90: # rotação completa em 90
			self.rotating = False	# indica que a animação terminou
			self.theta = 0		# zera o angulo da rotação
			self.update_colors() 	# atualiza cores
			glutIdleFunc(None) 		# termina a recursão

		glutPostRedisplay() # avisa ao OpenGl para atualizar a tela

	# a tranformação da rotação propriamente dita 
	def rotation(self):
		m, r = self.moves[-1][0], self.moves[-1][2] # pega o número e o eixo do move
		
		glPushMatrix()
		
		# transformação: translada para origem, rotaciona no eixo adequado,
		# e translada novamente para a posição inicial 
		glTranslatef(1.5,1.5,1.5)
		if r == 'z':
			glRotatef(self.theta,0,0,1)	# rotação no eixo Z
		elif r == 'x':
			glRotatef(self.theta,1,0,0)	# rotação no eixo X
		elif r == 'y':
			glRotatef(self.theta,0,1,0)	# rotação no eixo Y
		glTranslatef(-1.5,-1.5,-1.5)
	
		# somente desenha os cubos que fizerem parte do grupo especificado
		# por m, como a transformação já foi feita, os cubos em questão serão 
		# desenhados com um novo ângulo
		for j in self.move_type[m]:
			self.draw_a_cube(j)

			# salva os cubos rotacionados para que a função draw()
			# não os desenhem novamente e sem estarem rotacionados
			self.dont_draw.append(j) 

		glPopMatrix()
		glFlush()

	# atualiza as cores de acordo com a última rotação efetuadas
	def update_colors(self):
		
		m = self.moves[-1] # pega o último movimento

		top = self.top
		bottom = self.bottom
		front = self.front
		back = self.back
		right = self.right
		left = self.left

		if m[0] == 0 and m[1]: 			# rotação 0, inversa
			temp_a = top[0][0]
			temp_b = top[0][1]
			temp_c = top[0][2]

			top[0][0] = left[0][2]
			top[0][1] = left[1][2]
			top[0][2] = left[2][2]

			left[2][2] = bottom[2][0]
			left[1][2] = bottom[2][1]
			left[0][2] = bottom[2][2]

			bottom[2][0] = right[0][0]
			bottom[2][1] = right[1][0]
			bottom[2][2] = right[2][0]

			right[2][0] = temp_a
			right[1][0] = temp_b 
			right[0][0] = temp_c

			temp_a = front[2][0]
			temp_b = front[1][0]
			temp_c = front[0][0]

			front[2][0] = front[0][0]
			front[1][0] = front[0][1]
			front[0][0] = front[0][2]

			front[0][0] = front[0][2]
			front[0][1] = front[1][2]
			front[0][2] = front[2][2]

			front[0][2] = front[2][2]
			front[1][2] = front[2][1]
			front[2][2] = front[2][0]

			front[2][2] = temp_a
			front[2][1] = temp_b
			front[2][0] = temp_c

		elif m[0] == 0 and not m[1]: 	# rotação 0, não inversa
			temp_a = top[0][0]
			temp_b = top[0][1]
			temp_c = top[0][2]

			top[0][0] = right[2][0]
			top[0][1] = right[1][0]
			top[0][2] = right[0][0]

			right[0][0] = bottom[2][0]
			right[1][0] = bottom[2][1]
			right[2][0] = bottom[2][2]

			bottom[2][0] = left[2][2]
			bottom[2][1] = left[1][2]
			bottom[2][2] = left[0][2]

			left[0][2] = temp_a
			left[1][2] = temp_b 
			left[2][2] = temp_c

			temp_a = front[0][0]
			temp_b = front[1][0]
			temp_c = front[2][0]

			front[0][0] = front[2][0]
			front[1][0] = front[2][1]
			front[2][0] = front[2][2]

			front[2][0] = front[2][2]
			front[2][1] = front[1][2]
			front[2][2] = front[0][2]

			front[2][2] = front[0][2]
			front[1][2] = front[0][1]
			front[0][2] = front[0][0]

			front[0][2] = temp_a
			front[0][1] = temp_b
			front[0][0] = temp_c

		elif m[0] == 1 and m[1]:		# rotação 1, inversa
			temp_a = top[1][0]
			temp_b = top[1][1]
			temp_c = top[1][2]

			top[1][0] = left[0][1]
			top[1][1] = left[1][1]
			top[1][2] = left[2][1]

			left[2][1] = bottom[1][0]
			left[1][1] = bottom[1][1]
			left[0][1] = bottom[1][2]

			bottom[1][0] = right[0][1]
			bottom[1][1] = right[1][1]
			bottom[1][2] = right[2][1]

			right[2][1] = temp_a
			right[1][1] = temp_b 
			right[0][1] = temp_c

		elif m[0] == 1 and not m[1]: 	# rotação 1, não inversa
			temp_a = top[1][0]
			temp_b = top[1][1]
			temp_c = top[1][2]

			top[1][2] = right[0][1]
			top[1][1] = right[1][1]
			top[1][0] = right[2][1]

			right[0][1] = bottom[1][0]
			right[1][1] = bottom[1][1]
			right[2][1] = bottom[1][2]

			bottom[1][2] = left[0][1]
			bottom[1][1] = left[1][1]
			bottom[1][0] = left[2][1]

			left[0][1] = temp_a
			left[1][1] = temp_b 
			left[2][1] = temp_c

		elif m[0] == 2 and m[1]: 		# rotação 2, inversa
			temp_a = top[2][0]
			temp_b = top[2][1]
			temp_c = top[2][2]

			top[2][0] = left[0][0]
			top[2][1] = left[1][0]
			top[2][2] = left[2][0]

			left[2][0] = bottom[0][0]
			left[1][0] = bottom[0][1]
			left[0][0] = bottom[0][2]

			bottom[0][0] = right[0][2]
			bottom[0][1] = right[1][2]
			bottom[0][2] = right[2][2]

			right[2][2] = temp_a
			right[1][2] = temp_b 
			right[0][2] = temp_c

			temp_a = back[2][0]
			temp_b = back[1][0]
			temp_c = back[0][0]

			back[2][0] = back[0][0]
			back[1][0] = back[0][1]
			back[0][0] = back[0][2]
			back[0][0] = back[0][2]
			back[0][1] = back[1][2]
			back[0][2] = back[2][2]
			back[0][2] = back[2][2]
			back[1][2] = back[2][1]
			back[2][2] = back[2][0]
			back[2][2] = temp_a
			back[2][1] = temp_b
			back[2][0] = temp_c

		elif m[0] == 2 and not m[1]: 	# rotação 2, não inversa
			temp_a = top[2][0]
			temp_b = top[2][1]
			temp_c = top[2][2]

			top[2][2] = right[0][2]
			top[2][1] = right[1][2]
			top[2][0] = right[2][2]

			right[0][2] = bottom[0][0]
			right[1][2] = bottom[0][1]
			right[2][2] = bottom[0][2]

			bottom[0][2] = left[0][0]
			bottom[0][1] = left[1][0]
			bottom[0][0] = left[2][0]

			left[0][0] = temp_a
			left[1][0] = temp_b 
			left[2][0] = temp_c

			temp_a = back[0][0]
			temp_b = back[1][0]
			temp_c = back[2][0]

			back[0][0] = back[2][0]
			back[1][0] = back[2][1]
			back[2][0] = back[2][2]
			back[2][0] = back[2][2]
			back[2][1] = back[1][2]
			back[2][2] = back[0][2]
			back[2][2] = back[0][2]
			back[1][2] = back[0][1]
			back[0][2] = back[0][0]
			back[0][2] = temp_a
			back[0][1] = temp_b
			back[0][0] = temp_c

		elif m[0] == 3 and m[1]: 		# rotação 3, inversa
			temp_a = top[0][2]
			temp_b = top[1][2]
			temp_c = top[2][2]

			top[0][2] = front[0][2]
			top[1][2] = front[1][2]
			top[2][2] = front[2][2]

			front[0][2] = bottom[0][2]
			front[1][2] = bottom[1][2]
			front[2][2] = bottom[2][2]

			bottom[2][2] = back[0][2]
			bottom[1][2] = back[1][2]
			bottom[0][2] = back[2][2]

			back[2][2] = temp_a
			back[1][2] = temp_b 
			back[0][2] = temp_c

			temp_a = right[2][0]
			temp_b = right[1][0]
			temp_c = right[0][0]

			right[2][0] = right[0][0]
			right[1][0] = right[0][1]
			right[0][0] = right[0][2]

			right[0][0] = right[0][2]
			right[0][1] = right[1][2]
			right[0][2] = right[2][2]

			right[0][2] = right[2][2]
			right[1][2] = right[2][1]
			right[2][2] = right[2][0]

			right[2][2] = temp_a
			right[2][1] = temp_b
			right[2][0] = temp_c

		elif m[0] == 3 and not m[1]: 	# rotação 3, não inversa
			temp_a = top[0][2]
			temp_b = top[1][2]
			temp_c = top[2][2]

			top[2][2] = back[0][2]
			top[1][2] = back[1][2]
			top[0][2] = back[2][2]

			back[2][2] = bottom[0][2]
			back[1][2] = bottom[1][2]
			back[0][2] = bottom[2][2]

			bottom[0][2] = front[0][2]
			bottom[1][2] = front[1][2]
			bottom[2][2] = front[2][2]

			front[0][2] = temp_a
			front[1][2] = temp_b 
			front[2][2] = temp_c

			temp_a = right[0][0]
			temp_b = right[1][0]
			temp_c = right[2][0]

			right[0][0] = right[2][0]
			right[1][0] = right[2][1]
			right[2][0] = right[2][2]

			right[2][0] = right[2][2]
			right[2][1] = right[1][2]
			right[2][2] = right[0][2]

			right[2][2] = right[0][2]
			right[1][2] = right[0][1]
			right[0][2] = right[0][0]

			right[0][2] = temp_a
			right[0][1] = temp_b
			right[0][0] = temp_c
		
		elif m[0] == 4 and m[1]: 		# rotação 4, inversa
			temp_a = top[0][1]
			temp_b = top[1][1]
			temp_c = top[2][1]

			top[0][1] = front[0][1]
			top[1][1] = front[1][1]
			top[2][1] = front[2][1]

			front[0][1] = bottom[0][1]
			front[1][1] = bottom[1][1]
			front[2][1] = bottom[2][1]

			bottom[2][1] = back[0][1]
			bottom[1][1] = back[1][1]
			bottom[0][1] = back[2][1]

			back[2][1] = temp_a
			back[1][1] = temp_b 
			back[0][1] = temp_c
		
		elif m[0] == 4 and not m[1]: 	# rotação 4, não inversa
			temp_a = top[0][1]
			temp_b = top[1][1]
			temp_c = top[2][1]

			top[2][1] = back[0][1]
			top[1][1] = back[1][1]
			top[0][1] = back[2][1]

			back[2][1] = bottom[0][1]
			back[1][1] = bottom[1][1]
			back[0][1] = bottom[2][1]

			bottom[0][1] = front[0][1]
			bottom[1][1] = front[1][1]
			bottom[2][1] = front[2][1]

			front[0][1] = temp_a
			front[1][1] = temp_b 
			front[2][1] = temp_c
		
		elif m[0] == 5 and m[1]: 		# rotação 5, inversa
			temp_a = top[0][0]
			temp_b = top[1][0]
			temp_c = top[2][0]

			top[0][0] = front[0][0]
			top[1][0] = front[1][0]
			top[2][0] = front[2][0]

			front[0][0] = bottom[0][0]
			front[1][0] = bottom[1][0]
			front[2][0] = bottom[2][0]

			bottom[2][0] = back[0][0]
			bottom[1][0] = back[1][0]
			bottom[0][0] = back[2][0]

			back[2][0] = temp_a
			back[1][0] = temp_b 
			back[0][0] = temp_c

			temp_a = left[0][0]
			temp_b = left[1][0]
			temp_c = left[2][0]

			left[0][0] = left[2][0]
			left[1][0] = left[2][1]
			left[2][0] = left[2][2]

			left[2][0] = left[2][2]
			left[2][1] = left[1][2]
			left[2][2] = left[0][2]

			left[2][2] = left[0][2]
			left[1][2] = left[0][1]
			left[0][2] = left[0][0]

			left[0][2] = temp_a
			left[0][1] = temp_b
			left[0][0] = temp_c
		
		elif m[0] == 5 and not m[1]: 	# rotação 5, não inversa
			temp_a = top[0][0]
			temp_b = top[1][0]
			temp_c = top[2][0]

			top[2][0] = back[0][0]
			top[1][0] = back[1][0]
			top[0][0] = back[2][0]

			back[2][0] = bottom[0][0]
			back[1][0] = bottom[1][0]
			back[0][0] = bottom[2][0]

			bottom[0][0] = front[0][0]
			bottom[1][0] = front[1][0]
			bottom[2][0] = front[2][0]

			front[0][0] = temp_a
			front[1][0] = temp_b 
			front[2][0] = temp_c

			temp_a = left[2][0]
			temp_b = left[1][0]
			temp_c = left[0][0]

			left[2][0] = left[0][0]
			left[1][0] = left[0][1]
			left[0][0] = left[0][2]

			left[0][0] = left[0][2]
			left[0][1] = left[1][2]
			left[0][2] = left[2][2]

			left[0][2] = left[2][2]
			left[1][2] = left[2][1]
			left[2][2] = left[2][0]

			left[2][2] = temp_a
			left[2][1] = temp_b
			left[2][0] = temp_c
		
		elif m[0] == 6 and m[1]: 		# rotação 6, inversa
			temp_a = back[2][0]
			temp_b = back[2][1]
			temp_c = back[2][2]

			back[2][2] = left[2][0]
			back[2][1] = left[2][1]
			back[2][0] = left[2][2]

			left[2][0] = front[2][0]
			left[2][1] = front[2][1]
			left[2][2] = front[2][2]

			front[2][0] = right[2][0]
			front[2][1] = right[2][1]
			front[2][2] = right[2][2]

			right[2][2] = temp_a
			right[2][1] = temp_b 
			right[2][0] = temp_c

			temp_a = top[2][0]
			temp_b = top[1][0]
			temp_c = top[0][0]

			top[2][0] = top[0][0]
			top[1][0] = top[0][1]	
			top[0][0] = top[0][2]

			top[0][0] = top[0][2]
			top[0][1] = top[1][2]
			top[0][2] = top[2][2]

			top[0][2] = top[2][2]
			top[1][2] = top[2][1]
			top[2][2] = top[2][0]

			top[2][2] = temp_a
			top[2][1] = temp_b
			top[2][0] = temp_c
		
		elif m[0] == 6 and not m[1]: 	# rotação 6, não inversa
			temp_a = back[2][0]
			temp_b = back[2][1]
			temp_c = back[2][2]

			back[2][2] = right[2][0]
			back[2][1] = right[2][1]
			back[2][0] = right[2][2]

			right[2][0] = front[2][0]
			right[2][1] = front[2][1]
			right[2][2] = front[2][2]

			front[2][0] = left[2][0]
			front[2][1] = left[2][1]
			front[2][2] = left[2][2]

			left[2][2] = temp_a
			left[2][1] = temp_b 
			left[2][0] = temp_c

			temp_a = top[0][0]
			temp_b = top[1][0]
			temp_c = top[2][0]

			top[0][0] = top[2][0]
			top[1][0] = top[2][1]
			top[2][0] = top[2][2]

			top[2][0] = top[2][2]
			top[2][1] = top[1][2]
			top[2][2] = top[0][2]

			top[2][2] = top[0][2]
			top[1][2] = top[0][1]
			top[0][2] = top[0][0]

			top[0][2] = temp_a
			top[0][1] = temp_b
			top[0][0] = temp_c
		
		elif m[0] == 7 and m[1]: 		# rotação 7, inversa
			temp_a = back[1][0]
			temp_b = back[1][1]
			temp_c = back[1][2]

			back[1][2] = left[1][0]
			back[1][1] = left[1][1]
			back[1][0] = left[1][2]

			left[1][0] = front[1][0]
			left[1][1] = front[1][1]
			left[1][2] = front[1][2]

			front[1][0] = right[1][0]
			front[1][1] = right[1][1]
			front[1][2] = right[1][2]

			right[1][2] = temp_a
			right[1][1] = temp_b 
			right[1][0] = temp_c
		
		elif m[0] == 7 and not m[1]: 	# rotação 7, não inversa
			temp_a = back[1][0]
			temp_b = back[1][1]
			temp_c = back[1][2]

			back[1][2] = right[1][0]
			back[1][1] = right[1][1]
			back[1][0] = right[1][2]

			right[1][0] = front[1][0]
			right[1][1] = front[1][1]
			right[1][2] = front[1][2]

			front[1][0] = left[1][0]
			front[1][1] = left[1][1]
			front[1][2] = left[1][2]

			left[1][2] = temp_a
			left[1][1] = temp_b 
			left[1][0] = temp_c
		
		elif m[0] == 8 and m[1]: 		# rotação 8, inversa
			temp_a = back[0][0]
			temp_b = back[0][1]
			temp_c = back[0][2]

			back[0][2] = left[0][0]
			back[0][1] = left[0][1]
			back[0][0] = left[0][2]

			left[0][0] = front[0][0]
			left[0][1] = front[0][1]
			left[0][2] = front[0][2]

			front[0][0] = right[0][0]
			front[0][1] = right[0][1]
			front[0][2] = right[0][2]

			right[0][2] = temp_a
			right[0][1] = temp_b 
			right[0][0] = temp_c

			temp_a = bottom[0][0]
			temp_b = bottom[1][0]
			temp_c = bottom[2][0]

			bottom[0][0] = bottom[2][0]
			bottom[1][0] = bottom[2][1]
			bottom[2][0] = bottom[2][2]

			bottom[2][0] = bottom[2][2]
			bottom[2][1] = bottom[1][2]
			bottom[2][2] = bottom[0][2]

			bottom[2][2] = bottom[0][2]
			bottom[1][2] = bottom[0][1]
			bottom[0][2] = bottom[0][0]

			bottom[0][2] = temp_a
			bottom[0][1] = temp_b
			bottom[0][0] = temp_c

		elif m[0] == 8 and not m[1]: 	# rotação 8, não inversa
			temp_a = back[0][0]
			temp_b = back[0][1]
			temp_c = back[0][2]

			back[0][2] = right[0][0]
			back[0][1] = right[0][1]
			back[0][0] = right[0][2]

			right[0][0] = front[0][0]
			right[0][1] = front[0][1]
			right[0][2] = front[0][2]

			front[0][0] = left[0][0]
			front[0][1] = left[0][1]
			front[0][2] = left[0][2]

			left[0][2] = temp_a
			left[0][1] = temp_b 
			left[0][0] = temp_c

			temp_a = bottom[2][0]
			temp_b = bottom[1][0]
			temp_c = bottom[0][0]

			bottom[2][0] = bottom[0][0]
			bottom[1][0] = bottom[0][1]	
			bottom[0][0] = bottom[0][2]

			bottom[0][0] = bottom[0][2]
			bottom[0][1] = bottom[1][2]
			bottom[0][2] = bottom[2][2]

			bottom[0][2] = bottom[2][2]
			bottom[1][2] = bottom[2][1]
			bottom[2][2] = bottom[2][0]

			bottom[2][2] = temp_a
			bottom[2][1] = temp_b
			bottom[2][0] = temp_c

		else:
			pass

	# desenha o cubo com as cores e transformações necessárias
	def draw(self):
		if self.moves: # ocorreu algum move?

			# se ainda estiver rodando, continua rodando
			if self.rotating:
				self.rotation()

			# desenha o resto dos cubos que não fazem da parte da rotação
			glPushMatrix()
			for i in xrange(27):
				if i not in self.dont_draw:
					self.draw_a_cube(i) # desenha somente os que não estão na rotação
			
			# se chegou até aqui, toda a rotação necessária foi feita, portanto 
			# o vetor deve ficar vazio para que, pelo menos até a próxima 
			# rotação, o cubo seja desenhado inteiro
			self.dont_draw = []
			
			glPopMatrix()
			glFlush()

		else:
			for i in xrange(27): # desenho inicial
				self.draw_a_cube(i)

	# desenha o i-ésimo cubo
	def draw_a_cube(self, i):

		p = self.org_cubes[i]			   # pega a coordenada do ponto de orig. do cubo
		c = self.get_colors(i)			   # pega as cores das faces

		# face para -z
		glBegin(GL_POLYGON)				   # preenche o espaço entre os vert. com polígonos
		glNormal3f(0,0,-1) 				   # normal da face
		glColor3fv(self.colors[c[0]])
		glVertex3f(  p[0],   p[1],   p[2]) # 0,0,0
		glVertex3f(  p[0], p[1]+1,   p[2]) # 0,1,0
		glVertex3f(p[0]+1, p[1]+1,   p[2]) # 1,1,0
		glVertex3f(p[0]+1,   p[1],   p[2]) # 1,0,0
		glEnd()

		# face pra +z
		glBegin(GL_POLYGON)
		glNormal3f(0,0,1)
		glColor3fv(self.colors[c[1]])
		glVertex3f(  p[0],   p[1], p[2]+1) # 0,0,1
		glVertex3f(  p[0], p[1]+1, p[2]+1) # 0,1,1
		glVertex3f(p[0]+1, p[1]+1, p[2]+1) # 1,1,1
		glVertex3f(p[0]+1,   p[1], p[2]+1) # 1,0,1
		glEnd()

		# face pra -x
		glBegin(GL_POLYGON)
		glNormal3f(-1,0,0)
		glColor3fv(self.colors[c[2]])
		glVertex3f(  p[0],   p[1], p[2]+1) # 0,0,1
		glVertex3f(  p[0], p[1]+1, p[2]+1) # 0,1,1
		glVertex3f(  p[0], p[1]+1,   p[2]) # 0,1,0
		glVertex3f(  p[0],   p[1],   p[2]) # 0,0,0
		glEnd()

		# face pra +x
		glBegin(GL_POLYGON)
		glNormal3f(1,0,0)
		glColor3fv(self.colors[c[3]])
		glVertex3f(p[0]+1,   p[1], p[2]+1) # 1,0,1
		glVertex3f(p[0]+1, p[1]+1, p[2]+1) # 1,1,1
		glVertex3f(p[0]+1, p[1]+1,   p[2]) # 1,1,0
		glVertex3f(p[0]+1,   p[1],   p[2]) # 1,0,0
		glEnd()

		# face pra -y
		glBegin(GL_POLYGON)
		glNormal3f(0,-1,0)
		glColor3fv(self.colors[c[4]])
		glVertex3f(  p[0],   p[1],   p[2]) # 0,0,0
		glVertex3f(  p[0],   p[1], p[2]+1) # 0,0,1
		glVertex3f(p[0]+1,   p[1], p[2]+1) # 1,0,1
		glVertex3f(p[0]+1,   p[1],   p[2]) # 1,0,0
		glEnd()
		
		# face pra y
		glBegin(GL_POLYGON)
		glNormal3f(0,1,0)
		glColor3fv(self.colors[c[5]])
		glVertex3f(  p[0], p[1]+1,   p[2]) # 0,1,0
		glVertex3f(  p[0], p[1]+1, p[2]+1) # 0,1,1
		glVertex3f(p[0]+1, p[1]+1, p[2]+1) # 1,1,1
		glVertex3f(p[0]+1, p[1]+1,   p[2]) # 1,1,0
		glEnd()

		self.draw_edges(i)

		# pega as cores de cada 1/9 de cada face, ela
	
	# retorna um vetor 6x9 contendo os indices para
	# para a posição do vetor COLORS que corresponde
	# a cor adequada
	def get_colors(self, i):
		temp = [6 for x in xrange(6)]
		
		if i == 0:
			temp[0] = self.back[0][0]		# 0|0|0
			temp[2] = self.left[0][0]		# 0|0|0 z0
			temp[4] = self.bottom[0][0]		# x|0|0
		elif i == 1:
			temp[0] = self.back[0][1]		# 0|0|0
			temp[4] = self.bottom[0][1]		# 0|0|0 z0
			# qq coisa pra não estragar 	# 0|x|0
		elif i == 2:
			temp[0] = self.back[0][2]		# 0|0|0
			temp[3] = self.right[0][2]		# 0|0|0 z0
			temp[4] = self.bottom[0][2]		# 0|0|x
		elif i == 3:
			temp[0] = self.back[1][0]		# 0|0|0
			temp[2] = self.left[1][0]		# x|0|0 z0
			# o comentario explicativo  	# 0|0|0
		elif i == 4:
			temp[0] = self.back[1][1]		# 0|0|0
											# 0|x|0 z0
											# 0|0|0
		elif i == 5:
			temp[0] = self.back[1][2]		# 0|0|0
			temp[3] = self.right[1][2]		# 0|0|x z0
											# 0|0|0
		elif i == 6:
			temp[0] = self.back[2][0]		# x|0|0
			temp[2] = self.left[2][0]		# 0|0|0 z0
			temp[5] = self.top[2][0]		# 0|0|0
		elif i == 7:
			temp[0] = self.back[2][1]		# 0|x|0
			temp[5] = self.top[2][1]		# 0|0|0 z0
											# 0|0|0
		elif i == 8:
			temp[0] = self.back[2][2]		# 0|0|x
			temp[3] = self.right[2][2]		# 0|0|0 z0
			temp[5] = self.top[2][2]		# 0|0|0
		elif i == 9:
			temp[2] = self.left[0][1]		# 0|0|0
			temp[4] = self.bottom[1][0]		# 0|0|0 z1
											# x|0|0
		elif i == 10:
			temp[4] = self.bottom[1][1]		# 0|0|0
											# 0|0|0 z1
											# 0|x|0
		elif i == 11:
			temp[3] = self.right[0][1]		# 0|0|0
			temp[4] = self.bottom[1][2]		# 0|0|0 z1
											# 0|0|x
		elif i == 12:
			temp[2] = self.left[1][1]		# 0|0|0
											# x|0|0 z1
											# 0|0|0
		elif i == 13:
			pass							# 0|0|0
											# 0|x|0 z1
											# 0|0|0
		elif i == 14:
			temp[3] = self.right[1][1]		# 0|0|0
											# 0|0|x z1
											# 0|0|0
		elif i == 15:
			temp[5] = self.top[1][0]		# x|0|0
			temp[2] = self.left[2][1]		# 0|0|0 z1
											# 0|0|0
		elif i == 16:
			temp[5] = self.top[1][1]		# 0|x|0
											# 0|0|0 z1
											# 0|0|0
		elif i == 17:
			temp[5] = self.top[1][2]		# 0|0|x
			temp[3] = self.right[2][1]		# 0|0|0 z1
											# 0|0|0
		elif i == 18:
			temp[1] = self.front[0][0]		# 0|0|0
			temp[2] = self.left[0][2]		# 0|0|0 z2
			temp[4] = self.bottom[2][0]		# x|0|0
		elif i == 19:
			temp[1] = self.front[0][1]		# 0|0|0
			temp[4] = self.bottom[2][1]		# 0|0|0 z2
											# 0|x|0
		elif i == 20:
			temp[1] = self.front[0][2]		# 0|0|0
			temp[3] = self.right[0][0]		# 0|0|0 z2
			temp[4] = self.bottom[2][2]		# 0|0|x
		elif i == 21:
			temp[1] = self.front[1][0]		# 0|0|0
			temp[2] = self.left[1][2]		# x|0|0 z2
											# 0|0|0
		elif i == 22:
			temp[1] = self.front[1][1]		# 0|0|0
											# 0|x|0 z2
											# 0|0|0
		elif i == 23:
			temp[1] = self.front[1][2]		# 0|0|0
			temp[3] = self.right[1][0]		# 0|0|x z2
											# 0|0|0
		elif i == 24:
			temp[1] = self.front[2][0]		# x|0|0
			temp[2] = self.left[2][2]		# 0|0|0 z2
			temp[5] = self.top[0][0]		# 0|0|0
		elif i == 25:
			temp[1] = self.front[2][1]		# 0|x|0
			temp[5] = self.top[0][1]		# 0|0|0 z2
											# 0|0|0
		elif i == 26:
			temp[1] = self.front[2][2]		# 0|0|x
			temp[3] = self.right[2][0]		# 0|0|0 z2
			temp[5] = self.top[0][2]		# 0|0|0

		return temp

	# desenha as arestas do i-ésimo cubo
	def draw_edges(self, i):

		p = self.org_cubes[i]

		glColor3f(0,0,0)
		glLineWidth(3.0)
		glBegin(GL_LINE_LOOP)
		glVertex3f(  p[0],   p[1],   p[2]) # 0,0,0
		glVertex3f(  p[0], 1+p[1],   p[2]) # 0,1,0
		glVertex3f(1+p[0], 1+p[1],   p[2]) # 1,1,0
		glVertex3f(1+p[0],   p[1],   p[2]) # 1,0,0
		glEnd()

		glBegin(GL_LINE_LOOP)
		glVertex3f(  p[0],   p[1], 1+p[2]) # 0,0,1
		glVertex3f(  p[0], 1+p[1], 1+p[2]) # 0,1,1
		glVertex3f(1+p[0], 1+p[1], 1+p[2]) # 1,1,1
		glVertex3f(1+p[0],   p[1], 1+p[2]) # 1,0,1
		glEnd()

		glBegin(GL_LINE_LOOP)
		glVertex3f(  p[0],   p[1], 1+p[2]) # 0,0,1
		glVertex3f(  p[0], 1+p[1], 1+p[2]) # 0,1,1
		glVertex3f(  p[0], 1+p[1],   p[2]) # 0,1,0
		glVertex3f(  p[0],   p[1],   p[2]) # 0,0,0
		glEnd()

		glBegin(GL_LINE_LOOP)
		glVertex3f(1+p[0],   p[1], 1+p[2]) # 1,0,1
		glVertex3f(1+p[0], 1+p[1], 1+p[2]) # 1,1,1
		glVertex3f(1+p[0], 1+p[1],   p[2]) # 1,1,0
		glVertex3f(1+p[0],   p[1],   p[2]) # 1,0,0
		glEnd()
		
		glBegin(GL_LINE_LOOP)
		glVertex3f(  p[0],   p[1],   p[2]) # 0,0,0
		glVertex3f(  p[0],   p[1], 1+p[2]) # 0,0,1
		glVertex3f(1+p[0],   p[1], 1+p[2]) # 1,0,1
		glVertex3f(1+p[0],   p[1],   p[2]) # 1,0,0
		glEnd()

		glBegin(GL_LINE_LOOP)
		glVertex3f(  p[0], 1+p[1],   p[2]) # 0,1,0
		glVertex3f(  p[0], 1+p[1], 1+p[2]) # 0,1,1
		glVertex3f(1+p[0], 1+p[1], 1+p[2]) # 1,1,1
		glVertex3f(1+p[0], 1+p[1],   p[2]) # 1,1,0
		glEnd()

	def display(self):

		glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		glEnable(GL_DEPTH_TEST)

		glLoadIdentity()

		glEnable(GL_NORMALIZE) # normaliza a normal de todo o objeto

		glShadeModel(GL_SMOOTH) # define que a "troca" de sombra deve ser suave (smooth)

		glLightfv(GL_LIGHT0, GL_DIFFUSE, self.light_diffuse) 	# luz básica
		glLightfv(GL_LIGHT0, GL_POSITION, self.light_position) 	# configura a posição da camera
		
		glEnable(GL_LIGHTING) 	# habilita a iluminação
		glEnable(GL_LIGHT0)		# "liga" a luz

		# ColorMaterial faz com que a cor dos objetos iluminados acompanhem a cor atual do objeto.
		# na prática, e explicando de maneira simples, essa técnica faz com que seja considerada
		# a cor definida por glColor3f, do contrário seria necessário o uso de combinações de luz
		# para definir a cor de cada objeto.
		glColorMaterial(GL_FRONT_AND_BACK, GL_DIFFUSE)
		glEnable(GL_COLOR_MATERIAL)

		glTranslatef(0, 0, self.pseudo_zoom)	# posição do mundo
		glRotatef(self.tipangle, 1,0,0)  		# Up e down inclina o mundo
		glRotatef(self.viewangle, 0,1,0) 	 	# Right/left gira o mundo

		glPushMatrix()

		glTranslatef(-1.5, -1.5, -1.5) # translada o *cubo* de modo a centralizá-lo no mundo
		self.draw()

		glPopMatrix()

		glutSwapBuffers()

def main():
	d = Drawing()

if __name__ == '__main__':
	main()
