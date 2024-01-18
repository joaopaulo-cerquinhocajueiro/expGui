# Experimenter

Programa arduino e interface gráfica para fazer experiências de controle.

A interface gráfica se comunica com o arduino para gerar testes de resposta ao degrau e reposta a sinais PRBS, em sistemas em malha aberta e em malha fachada com controladores PID e compensadores implementados no arduino.

![sistema.svg](sistema.svg)

## Arduino

O arduino é programado para receber e enviar pacotes pela interface serial. Um comando especial faz ele rodar um experimento, que consiste em comandar a variável controlada Vc e observar a variável observada Vo por um tempo T2.

A variável comandada é implementada por um sinal PWM gerado no pino 5 do arduino. Pela própria limitação do PWM do arduino, ela varia na faixa de 0 a 255 e é descrita internamente por um byte.

A variável observada é obtida pela entrada analógica A0. Como o arduino usa 10 bits para a entrada analógica na faixa de 0 a 5 V, seu valor fica internamente na faixa de 0 a 1023.

É ainda implementado um setpoint, lido na entrada A5, também na faixa de 0 a 1023.

### Experimentos

Os experimentos podem ser em malha aberta ou malha fechada. Em malha fechada pode-se implementar um controlador PID ou um compensador avanço/atraso. Além disso, em malha fechada o setpoint pode ser definido por software ou pela entrada de setpoint.
Tanto nas variáveis controladas em malha aberta quanto nos setpoints por software em malha fechada, pode-se implementar um sinal do tipo degrau ou um sinal do tipo PRBS.

O sinal do tipo degrau é da seguinte forma:

```
// V1        __________
//          |
//          |
// V0_______|
//   0      T1        T2
```

Enquanto que o sinal do tipo PRBS é da forma:
```
// V1       --------  ----   ---
//          |      |  |  |   | |
// V0--------      |  |  |   | |
//                 |  |  |   | |
// V2              ----  ----- ---
//   0      T1                   T2
```

onde V0, V1 e V2 são ajustáveis (entre 0 e 255 para malha aberta ou 0 e 1023 para malha fechada), assim como T1 e T2.

Os tempos são definidos como valores discretos de número de passos. Por default o tempo de passo, Ts, é de 10 ms.
 
O sinal PRBS gera pulsos entre V1 e V2 de comprimento aleatório, entre Tmin e Tmax, também ajustáveis.

### Pacotes
A comunicação é do tipo mestre-escravo: o arduino só responde a um comando do computador
```mermaid
sequenceDiagram
    Computador ->> Arduino: Comando
    Arduino-->>Computador: Resposta
```
Os comandos enviados pelo computador são do formato:

```
// ________________________
// | type | payload | EOP |
// ------------------------
```
Onde "type" é uma letra que define o tipo do pacote, "payload" é dependente do tipo, podendo inclusive não ter;  e "EOP" é o terminador, escolhido como o valor 55 (ascii 7).

Os tipos de pacote enviados para o arduino podem ser:

- R - para iniciar um experimento. Sem payload.
- M - para definir o tipo, ou o modo, do experimento. Seu payload é um byte, que pode ser:
	- 0 - resposta ao degrau em malha aberta
	- 1 - resposta a PRBS em malha aberta
	- 2 - controle PID com setpoint por entrada
	- *3 - controle com compensador com setpoint por entrada*
	- *4 - resposta ao degrau com controle PID*
	- *5 - resposta ao degrau com compensador*
	- *6 - resposta a PRBS com controle PID*
	- *7 - resposta a PRBS com compensador*
	
	(*os em itálico ainda não estão implementados*)
- V - para definir os valores das variáveis controladas usadas no experimento. O payload são três valores de dois bytes: V0, V1 e V2.

- T - para definir as constantes de tempo do experimento. O payload são dois valores de 2 bytes: T0 e T1. Estes valores são definidos em número de steps (50 steps por segundo por default).
```
//            ---------------
// __________/
// 0         T0             T1
```

- B - para definir o tempo mínimo e o tempo máximo dos pulsos PRBS. O payload são dois valores de 2 bytes: Tmin e Tmax. Estes valores são definidos em número de steps (50 steps por segundo por default).

- Q - para definir os valores das constantes do PID - Kp, Ki e Kd. Cada valor é enviado como float32 dividido em 4 bytes em little endian.