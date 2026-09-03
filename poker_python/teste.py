from carta import Carta
from avaliador_de_maos import AvaliadorDeMaos

print("\n--- TESTE 5: O BUG DO STRAIGHT FLUSH FANTASMA (A-2-3-4-5) ---")

# Criamos uma mão com um Straight Flush de Espadas (A, 2, 3, 4, 5)
# E duas cartas de naipes diferentes para completar as 7 cartas (Mesa + Mão)
cartas_teste = [
    Carta(14, '♠️'), # Ás de Espadas
    Carta(5, '♠️'),  # 5 de Espadas
    Carta(4, '♠️'),  # 4 de Espadas
    Carta(3, '♠️'),  # 3 de Espadas
    Carta(2, '♠️'),  # 2 de Espadas
    Carta(10, '♥️'), # Lixo
    Carta(9, '♣️')   # Lixo
]

print("Cartas na mesa/mão:")
for c in cartas_teste:
    print(c.retornar_carta(), end=" ")
print("\n")

print("1. Avaliando se é Sequência normal...")
eh_seq = AvaliadorDeMaos.eh_sequencia(cartas_teste)
print(f"Resultado: {eh_seq} (Esperado: True)")

print("\n2. Avaliando se é Straight Flush...")
eh_sf = AvaliadorDeMaos.eh_straight_flush(cartas_teste)

if eh_sf:
    print("✅ SUCESSO: O programa reconheceu o Straight Flush (A-2-3-4-5)!")
else:
    print(f"Resultado: {eh_sf} (Esperado: True)")
    print("❌ FALHA DETECTADA: O programa NÃO reconheceu o Straight Flush.")
    print("   Motivo: Ele achou o Flush de espadas. Depois contou as cartas 5, 4, 3, 2 (4 cartas)")
    print("   e parou, esquecendo que o Ás(14) também funciona como '1'.")