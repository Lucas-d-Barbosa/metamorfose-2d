Documento de Game Design (GDD) – Metamorfose 2D
1. Visão Geral do Projeto
Metamorfose 2D é um jogo 2D para PC desenvolvido em Pygame, focado em stealth, escalada, sobrevivência e degradação sensorial, adaptando fielmente a obra A Metamorfose, de Franz Kafka. O tom do jogo é claustrofóbico e melancólico, com forte ênfase em decisões diegéticas, consequências persistentes e dinâmicas de som.
Plataforma: Windows/Linux.
Público-alvo: 14+ (foco em narrativa e atmosfera).
Pilares de Design: Furtividade tensa, mobilidade vertical libertadora, recursos escassos, deterioração progressiva (física e sensorial) e fidelidade absoluta à cronologia narrativa original.
2. Sinopse e Adaptação
O jogo converte os capítulos do livro em fases distintas, estruturando o declínio de Gregor Samsa através de mecânicas de jogo. Personagens atuam como diferentes obstáculos na engine de furtividade:
Gregor: Personagem jogável. Transição de humano funcional para inseto debilitado e cego.
Grete (Irmã): Cuidadora inicial que se transforma na principal antagonista narrativa.
O Pai: Ameaça agressiva e imprevisível.
A Mãe: Obstáculo frágil (aciona penalidades de stealth extremas caso desmaie de susto).
O Gerente (Patrão): Obstáculo rápido de detecção na primeira fase.
Três Inquilinos: Patrulha rígida, campo de visão estendido, representam o Game Over imediato nas fases finais.
A Faxineira: NPC caótico que não gera Game Over, mas reposiciona o jogador à força (knockback).
3. Cronologia Narrativa e Fases
Fase 1: O Despertar e o Pânico (O Quarto)
Contexto: Manhã da transformação. O Gerente chega.
Gameplay: Tutorial de movimentação e furtividade básica. Gregor tenta destrancar a porta com a boca (minigame). A tentativa de comunicação verbal de Gregor gera chiados que aumentam o alerta dos NPCs (Comunicação Reversa). Culmina com a fuga do Gerente e o ataque do Pai, que empurra Gregor com uma bengala de volta ao quarto.
Fase 2: Adaptação e as Memórias (O Corredor)
Contexto: Descoberta das novas habilidades e perda da mobília.
Gameplay: Introdução da mecânica de teto (recuperação de estamina/zona de conforto). O jogador descobre que comida fresca causa repulsa e dano à estamina, enquanto lixo/comida estragada a restaura. A fase possui um evento de tempo/stealth: a Missão do Quadro. O jogador deve escalar e se posicionar sobre o quadro na parede sem assustar a Mãe. O sucesso preserva a memória humana; a falha impacta o diálogo final.
Fase 3: A Agressão e a Deterioração (A Sala)
Contexto: Picos de agressividade do pai e a transformação do quarto de Gregor em um depósito de tralhas.
Gameplay: O quarto recebe lixo interativo que, se atravessado, levanta poeira e faz Gregor tossir (gerando ruído). O Field of View (FOV) do jogador sofre redução (Miopia Progressiva). O clímax da fase envolve desviar dos objetos arremessados pelo pai. A Maçã Crítica é um projétil único; falhar em desviar crava a maçã nas costas, aplicando um debuff permanente na estamina e velocidade até o fim do jogo.
Fase 4: A Música e a Morte (O Clímax)
Contexto: A casa alugada aos Inquilinos. A faxineira assume os cuidados.
Gameplay: O jogador está debilitado. As rotas normais estão bloqueadas pela Faxineira, que varre Gregor (knockback) sem alertar os outros. A adição das Zonas de Escuta permite a Gregor ouvir conversas através da parede para entender o estado da família. Os Três Inquilinos patrulham a sala em sincronia com FOV alto. O objetivo final é seguir o Áudio Direcional do Violino tocado por Grete até a porta da sala. A detecção culmina na sentença final de Grete e no fim trágico.
4. Requisitos Funcionais
Movimentação e Física
RF001: O sistema de movimentação utiliza WASD, com física 2D de aceleração e colisão em malha (grid).
RF002: O jogador deve poder transitar de forma fluida (sem snapping brusco) do chão para as paredes e teto.
RF003: O consumo de estamina no teto deve ser 50% menor em relação ao chão. Quedas forçadas devem gerar um evento de ruído em área (AoE Noise).
RF004: Áreas específicas (frestas e debaixo de móveis) devem permitir a passagem/ocultação do jogador, mudando seu estado para "oculto".
Stealth, Visão e Som
RF005: NPCs devem possuir cones de visão (FOV) e Linha de Visão (LoS) baseados em projeção de raios (Raycasting), bloqueados por paredes e móveis opacos.
RF006 (Comunicação Reversa): O input de interação/fala emite um balão de texto legível para o jogador, mas gera uma onda sonora circular que aumenta o estado de alerta de NPCs próximos em 50%.
RF007 (Miopia Progressiva): A câmera do jogador deve renderizar uma máscara de alpha (Fog of War) que reduz o campo de visão periférico gradativamente (100% na Fase 1, 60% na Fase 3, 40% na Fase 4), mantendo a UI inalterada.
RF008 (Zonas de Escuta): Triggers invisíveis próximos a paredes que, quando ativados por inatividade do jogador, exibem legendas de diálogos ocultos e atualizam flags no save state.
Sobrevivência e Ambiente
RF009: Barras de Fome e Estamina devem decair com movimento.
RF010: Itens do tipo "Comida Fresca" devem zerar a recuperação e tocar animação de repulsa. Itens "Comida Estragada" restauram de 20% a 30% da barra.
RF011: O quarto nas Fases 3 e 4 deve conter hitboxes de lixo. Permanecer nessas áreas por mais de 1.5s aciona um evento sonoro de tosse.
Narrativa e Eventos Críticos
RF012 (O Quadro): Evento engatilhado pela entrada da Mãe/Irmã no quarto. Inclui temporizador. Posição correta altera flag booleana saved_picture.
RF013 (A Maçã): Sistema de colisão de projéteis. Colisão com a "Maçã Crítica" atualiza o sprite do jogador e altera os valores máximos de estamina (-50%) e velocidade (-30%) no arquivo JSON de save.
RF014: A NPC Faxineira deve aplicar física de knockback ao colidir com o jogador, empurrando-o na direção oposta sem alterar o estado global de alerta da casa.
RF015: O áudio do violino na Fase 4 deve utilizar panning e volume baseados na distância entre o jogador e a porta da sala para guiar a navegação.
5. Histórias de Usuário
Como jogador, quero que tentar falar aumente o pânico dos NPCs, para entender a frustração da incomunicabilidade de Gregor.
Como jogador, quero usar o teto como zona de baixo consumo de estamina, para planejar rotas seguras e recuperar fôlego.
Como jogador, quero distinguir visualmente comida fresca de comida estragada, para gerenciar minha sobrevivência sem sofrer repulsa.
Como jogador, quero proteger o quadro posicionando-me sobre ele a tempo, para preservar a memória humana de Gregor antes que a Mãe o leve.
Como jogador, quero que minha visão de jogo diminua nas fases finais, para sentir a degradação física do personagem.
Como jogador, quero que a falha em esquivar da maçã cause um debuff permanente, refletindo a infecção letal descrita no livro.
Como jogador, quero encontrar zonas de escuta seguras nas paredes, para bisbilhotar as conversas e entender o contexto financeiro da família.
Como jogador, quero evitar as poeiras de lixo no meu próprio quarto, para não tossir e revelar minha posição durante a patrulha.
Como jogador, quero que a Faxineira me empurre fisicamente sem causar Game Over, para lidar com um tipo diferente de risco ambiental.
Como jogador, quero me orientar pelo som espacial do violino, para encontrar o caminho correto na reta final do jogo.
6. Tasks Técnicas por Sprints (Roadmap Macro – 22 Semanas)
Sprints 1–2 (Fundação): Setup de ambiente Pygame, manipulação de inputs, física 2D básica, colisões de cenário, transição chão/parede/teto e mecânica de frestas.
Sprints 3–4 (Stealth e Som): Algoritmo de projeção de LoS/FOV em grid, propagação de ruído (Voice Mechanic / AoE Noise), cálculo de colisão da onda sonora com a malha da IA e criação do HUD de Stealth.
Sprints 5–6 (Física e Sobrevivência): Multiplicadores de estamina baseados no estado da gravidade (is_grounded, is_ceiling). Sistema de fome, diferenciação de itens (fresco vs. podre), feedbacks visuais e balanceamento.
Sprints 7–8 (Fase 1 e Interações): Destrancar porta com a boca (minigame), rotinas de IA para o Gerente e o Pai, cutscenes de transição e introdução do sistema de diálogos.
Sprints 9–10 (Ambiente Dinâmico e Missões): Criação das máscaras de alpha (blend modes) para a miopia progressiva. Lógica da Missão do Quadro (temporizadores, pathfinding da Grete/Mãe, triggers de desmaio).
Sprints 11–12 (Combate Defensivo): Sistema de projéteis (Pai), Hitboxes e i-frames. Lógica da "Maçã Crítica", aplicação de debuff persistente, troca de spritesheet e atualização visual do HUD.
Sprints 13–15 (IA Complexa e Lixo): Implementação dos props de lixo com gerador de partículas e atraso (delta time) para acionar a tosse. Codificação dos Três Inquilinos (patrulha sincronizada e alerta compartilhado) e do comportamento de knockback da Faxineira.
Sprints 16–18 (Zonas de Escuta e Áudio): Raycasting/Colliders de área para as Zonas de Escuta. Sistema de áudio posicional para o Violino. Estruturação do objetivo final da porta da sala e cutscene de encerramento.
Sprints 19–22 (Polimento e QA): Integração narrativa completa. Serialização de dados (Save/Load em JSON mapeando flags de história e debuffs). Bateria de testes QA. Filtros de acessibilidade (daltonismo, remapeamento) e otimização de performance.
7. Critérios de Aceitação (Foco em QA)
Movimentação e Teto: A transição chão/parede/teto deve ocorrer sem que a hitbox do personagem atravesse polígonos sólidos (clipping). A taxa de consumo de estamina no teto deve ser validada no depurador como exatamente 50% do valor base.
Comunicação Reversa: O comando de "Fala" deve alterar instantaneamente o estado da máquina de IA do Gerente/Pai de "Patrulha" para "Alerta" caso estejam dentro do raio do som. O som não deve atravessar paredes com a flag "isolante".
Degradação Visual (Miopia): A máscara de Fog of War deve ser carregada corretamente após um Load Save dependendo da fase atual. UI, HUD de Alerta e Balões de Texto devem ser renderizados obrigatoriamente acima da camada de miopia.
Missão do Quadro: O evento deve possuir temporizador visível ou sonoro. O sucesso deve gravar saved_picture: true no JSON. Se o jogador for detectado no cone de visão da Mãe, a animação de desmaio deve ocorrer, cancelando o evento.
A Maçã Crítica: Se atingido, o estado de debuff deve persistir através da morte do personagem, reinício da fase e recarregamento do jogo. O jogo deve continuar matematicamente possível de ser concluído mesmo com 50% a menos de estamina máxima.
Lixo e Tosse: Permanecer dentro da hitbox do lixo por > 1.5 segundos deve gerar um ruído com raio de atração 2x maior que o som de passos comuns.
Inquilinos e Faxineira: O FOV dos inquilinos deve ser 30% maior que o da família, comprovável via depuração visual (modo debug). A colisão com a faxineira não deve, em nenhuma hipótese, invocar a tela de Game Over, aplicando apenas física de repulsão.
Violino: O sistema de áudio deve alterar os canais (Esquerda/Direita) e o ganho dinamicamente com base nas coordenadas X e Y do jogador em relação à porta da sala.
8. Roteiro de Cutscenes e Diálogos (In-Game)
Esta seção detalha os diálogos, pensamentos e prompts visuais para estruturar a narrativa e alimentar o sistema de balões de texto do Pygame.
Fase 1: O Despertar e o Pânico
Contexto: Gregor acorda atrasado para pegar o trem das 5h. O jogador assume o controle no quarto trancado.
Cutscene Inicial (Tela Preta, apenas texto e som de chuva):
Gregor (Pensamento): "O que aconteceu comigo? Não é um sonho…"
Gregor (Pensamento): "Eu devia ter pegado o trem das cinco. O despertador não tocou?"
Diálogos In-Game (Fora da porta - Zonas de Escuta automáticas):
Mãe: "Gregor? São quase sete horas. Você não ia viajar?"
Pai (Batendo na porta): "Gregor! Gregor! O que está acontecendo aí?"
Grete (Sussurrando): "Gregor… você está se sentindo mal? Precisa de alguma coisa?"
Evento: A Chegada do Gerente (O alerta sobe):
Gerente (Voz autoritária além da porta): "Bom dia, Sr. e Sra. Samsa. O chefe me mandou vir pessoalmente verificar por que o senhor Gregor não apareceu no trem da manhã."
Pai: "Ele não está bem, senhor Gerente. Por que mais ele perderia um dia de trabalho?"
Mecânica de "Comunicação Reversa" (Sempre que o jogador aperta "Falar"):
Balão do Jogador (Visível apenas para o jogador): "Senhor Gerente, eu já estou abrindo! Tive um pequeno mal-estar, mas já passou!"
Efeito Sonoro: Chiado estridente de inseto.
Gerente (Reação ao ruído): "Vocês ouviram isso? Isso… não parecia uma voz humana."
Cutscene de Fim da Fase 1 (Após destravar a porta):
Gregor sai de perto da porta.
Gerente (Gritando): "Aaaah! O que é isso?! Meu Deus!" (Som de passos correndo e a porta da frente batendo).
Mãe: (Som de desmaio imediato).
Pai: "Volte para lá! Volte agora, seu monstro!" (Animação do pai brandindo a bengala, forçando Gregor para dentro e trancando a porta a chave).
Fase 2: Adaptação e as Memórias
Contexto: Dias se passaram. Gregor agora explora a casa à noite para buscar comida. A família decide tirar seus móveis.
Cutscene Inicial:
Grete (Entrando rápido e deixando um prato de leite): "Ele deve estar com tanta fome… deixei o leite fresquinho que ele sempre gostou." (Sai e tranca a porta).
Diálogos In-Game (Mecânica de Comida):
Ao interagir com o leite: Gregor (Pensamento): "Era minha bebida favorita… mas o cheiro… me dá nojo agora." (Perde estamina).
Ao interagir com restos podres: Gregor (Pensamento): "Um pedaço de queijo velho e um repolho murcho… Perfeito." (Ganha estamina).
Missão do Quadro (Início do Evento):
Mãe (Fora do quarto): "Tem certeza, Grete? Ele pode precisar dos móveis."
Grete: "Não, mãe. Ele precisa de espaço para rastejar pelas paredes. Vamos tirar o armário pesado primeiro."
Durante a Missão (Mãe e Grete patrulhando):
Mãe: "Tudo isso me lembra tanto de quando ele era o nosso Gregor… Minha nossa, e se ele não quiser que tiremos nada?"
Gregor (Pensamento - se posicionando no teto/parede): "Elas estão tirando tudo. O armário, a escrivaninha… Vão levar meu passado embora. Preciso salvar pelo menos o quadro da mulher de peles!"
Desfechos da Missão do Quadro:
Falha (Mãe vê Gregor): Mãe: "Ah… Gregor!" (Desmaia). / Grete: "Mãe! O que você fez com ela, seu monstro?!"
Sucesso (Gregor abraça o quadro escondido): Grete: "Acho que já tiramos o suficiente por hoje. Vem, mãe. Deixe esse quadro aí."
Fase 3: A Agressão e a Deterioração
Contexto: O quarto virou depósito. A visão encurta. O Pai chega estressado do novo emprego como porteiro de banco.
Cutscene Inicial:
Pai (Entrando em casa com o uniforme): "O que foi essa confusão? Ela desmaiou de novo?!"
Grete: "Foi ele, pai! Ele escapou do quarto!"
Pai: "Eu já disse para vocês! Eu sabia que isso ia acontecer!"
Diálogos In-Game (A Maçã Crítica):
Pai (Patrulhando e arremessando objetos): "Fique no seu canto! Não chegue perto da sua mãe!"
Gregor (Pensamento - Visão turva): "Não consigo ver direito. Ele está jogando… maçãs da fruteira?"
Desfecho da Maçã (Caso seja atingido):
Som forte de impacto e esmagamento.
Gregor (Pensamento): "Atingiu minhas costas. Uma dor terrível. Acho que quebrou minha carapaça… Não consigo me mover direito." (Aplica o Debuff Permanente).
Fase 4: A Música e a Morte
Contexto: O apartamento foi alugado a três senhores rigorosos. A família come na cozinha; os inquilinos, na sala. A sujeira toma conta de Gregor.
Diálogos In-Game (A Faxineira patrulhando):
Faxineira (Cutucando Gregor com a vassoura): "Anda, sai do meio do caminho, seu besouro velho. Não tenho medo de você, não."
Zonas de Escuta (Se escondendo atrás da parede da cozinha):
Pai: "O dinheiro mal dá para as contas. Tivemos que vender as joias da sua mãe."
Mãe: "Pelo menos os senhores inquilinos pagam adiantado. Mas eles são tão exigentes com a limpeza…"
O Clímax (O Violino):
(Som de violino começa a tocar à distância)
Inquilino 1: "Senhor Samsa! Essa música é irritante. Mande parar."
Pai: "Minha filha está apenas tocando no corredor…"
Gregor (Pensamento - sendo atraído): "Como eu posso ser um animal se a música me toca tanto? Quero chegar perto. Quero dizer à Grete que vou pagar os estudos dela no conservatório…"
Detecção Final (Fim da Fase e Game Over Narrativo):
Inquilino 2 (Vê Gregor entrando na sala iluminada): "O QUE É ISSO? Senhor Samsa! O senhor mantém um inseto imundo junto dos hóspedes?!"
Inquilino 3: "Isso é nojento! Exigimos rescisão imediata do contrato! Não pagaremos nada por este chiqueiro!" (Eles saem batendo a porta).
Cutscene Final (A Sentença):
(Sala silenciosa e escura)
Grete (Chorando, exausta): "Pai… Mãe… não podemos continuar assim. Eu não vou pronunciar o nome do meu irmão na frente desse monstro."
Grete: "Nós tentamos cuidar. Tentamos suportar. Mas precisamos nos livrar dele. Se fosse o Gregor de verdade, ele teria percebido que humanos e um animal como esse não podem viver juntos. Ele teria ido embora por conta própria."
Gregor (Pensamento se apagando, som enfraquecendo): "Ela tem razão. Minhas dores estão passando… Que a escuridão leve tudo logo…"
Cutscene Epílogo:
(Tela clara, som alegre de um bonde, dia ensolarado. Imagens estáticas em aquarela do exterior).
Pai: "Foi um dia difícil, mas vejam como o sol está lindo hoje."
Mãe: "Sim. Acho que podemos nos mudar para um apartamento menor, mais barato e mais ensolarado agora."
Pai: "E olhem para a nossa Grete. Apesar de tudo… nossa filha desabrochou e se tornou uma bela mulher. Logo teremos que arranjar um bom marido para ela."
Tela Preta: FIM.
9. Direção de Arte e Cenários (Pixel Art)
O estilo visual será em Pixel Art, com foco em iluminação dramática e paletas de cores que perdem a saturação conforme o jogo avança. Para reforçar a atmosfera opressiva, o jogo utilizará um filtro visual simulando a estética de monitores CRT — com scanlines (linhas de varredura) suaves, color bleeding (sangramento de cores típico de telas antigas) e uma leve curvatura nas bordas. Isso cria uma lente analógica e claustrofóbica, aprisionando o jogador na perspectiva de Gregor.
9.1. O Quarto de Gregor (A Zona Segura em Degradação)
O quarto sofre a maior transformação visual durante o jogo, refletindo o estado mental e físico do protagonista.
Fase 1 (O Quarto Humano):
Visual: Tons pastéis amarelados e papel de parede florido. Há amostras de tecidos de seu trabalho como caixeiro-viajante espalhadas sobre uma mesa de madeira envernizada. Uma cama desarrumada ocupa o centro. A luz da manhã entra pela janela, mostrando partículas de poeira.
Pixel Art: Contornos nítidos. O quadro da mulher com o boá de peles tem destaque na parede (usando um tom de dourado na moldura que destoa do resto do quarto).
Fase 2 (O Quarto Vazio):
Visual: A cama e as mesas foram removidas. Ficam apenas marcas retangulares mais limpas no papel de parede sujo onde os móveis costumavam ficar.
Pixel Art: O ambiente parece mais amplo, mas frio. A paleta muda para tons de cinza e azul pálido. As marcas de arranhões de Gregor começam a aparecer no gesso do teto e das paredes.
Fase 3 e 4 (O Depósito de Lixo):
Visual: O quarto perde toda a dignidade. Caixotes empilhados, vassouras velhas, latas de lixo e móveis quebrados formam um labirinto vertical.
Pixel Art: O chão está coberto por uma fina camada de fuligem. A luz da janela está bloqueada por sujeira no vidro (apoiando a mecânica de miopia). Sombras densas escondem os cantos. O filtro CRT fica levemente mais ruidoso aqui.
9.2. O Corredor (O Limiar do Perigo)
Visual: Um corredor longo e estreito que conecta o quarto de Gregor ao resto da casa. O piso é de taco de madeira (que range mecanicamente se pisado fora do modo stealth). Há um grande relógio de pêndulo cujos tique-taques marcam o ritmo das patrulhas.
Pixel Art: Altíssimo contraste. As portas dos outros cômodos projetam frestas de luz quente no chão escuro do corredor. As paredes são forradas com um papel de parede de listras verticais, acentuando a sensação de altura quando Gregor escala.
9.3. A Sala de Jantar e Estar (A Luz Proibida)
Visual: O cômodo mais detalhado e iluminado, representando a vida humana que Gregor não pode mais acessar. Cheio de móveis de carvalho pesado, um tapete felpudo e um lustre de cristal.
Pixel Art: Tons quentes de laranja e âmbar dominam o espaço. O lustre emite uma luz radial brilhante. Durante a Fase 4 (Inquilinos), a mesa está farta com assados e vinho (em pixels brilhantes), contrastando com a fome de Gregor. O tapete amortece os passos, alterando o feedback visual e sonoro da movimentação.
10. Narrativa Interna: Os Pensamentos de Gregor
Os balões de pensamento de Gregor são a principal ferramenta para gerar empatia. Eles aparecem no topo da tela com uma fonte serifada e trêmula (pixelada), em caixas de diálogo com bordas irregulares. Eles narram a transição de um trabalhador ansioso para um inseto guiado por instintos.
10.1. Reflexões sobre o Trabalho e Ansiedade Humana (Fase 1)
(Ao tentar levantar da cama): "Que profissão cansativa eu escolhi… Viajar dia sim, dia não. Se eu não tivesse que pagar a dívida dos meus pais, já teria pedido demissão há muito tempo."
(Ao ver o relógio ticking): "Seis e meia! O trem das sete é o último. O chefe vai gritar tanto… por que meu corpo não obedece?"
(Ao ouvir o Gerente): "Ele veio pessoalmente. Eles não têm um pingo de confiança em mim. Eu sou apenas uma máquina de fazer dinheiro para eles."
10.2. Instintos e a Perda da Humanidade (Fases 2 e 3)
(Ao tentar comer comida fresca): "Minha irmã trouxe meu prato favorito… mas o cheiro… me dá ânsia. Por que meu estômago rejeita isso?"
(Ao encontrar lixo/comida estragada): "Isso tem um cheiro forte… azedo… maravilhoso. Nunca pensei que lixo me daria tanta água na boca."
(Ao escalar o teto pela primeira vez): "O chão é tão frio e distante. Aqui em cima… a gravidade não me machuca. Eu me sinto quase… livre. Posso respirar."
(Quando a mãe tira os móveis): "Não! Deixem meu armário! Deixem minha escrivaninha! Foi nela que estudei… Se levarem tudo, eu vou esquecer quem eu fui!"
10.3. Sentimentos de Culpa e Melancolia (Fase 4)
(Ao ouvir a família discutindo dinheiro nas Zonas de Escuta): "Meu pai teve que voltar a trabalhar. Ele está tão velho… A culpa é minha. Eu falhei com eles."
(Ao ver a irmã o ignorar): "Ela não me olha mais nos olhos. Ela só empurra a comida com a vassoura e corre. O amor dela também secou."
(Ao ouvir o violino tocando): "Que som lindo… Eu planejava mandá-la para o conservatório no Natal. Eu ia anunciar na ceia. Como eu posso ser um monstro repulsivo, se essa música enche meu peito de tanta luz?"
(Pensamento final, antes da tela apagar): "Minha respiração está tão fraca. Não sinto mais raiva deles. Eu só… queria que eles fossem felizes. Eu preciso desaparecer para que eles possam viver."
