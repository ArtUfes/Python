/**
 * Audio Engine para o Poker VIP
 * Utiliza áudios reais de cassino (foley de cartas e fichas)
 * com suporte a pré-carregamento, variação de pitch sutil para naturalidade
 * e fallback procedural (Web Audio API) caso necessário.
 */

class AudioEngine {
  constructor() {
    this.muted = false;
    this.volume = 0.6;
    this.audioCache = {};

    // Mapeamento de sons reais
    this.soundSets = {
      cardSlide: [
        '/sounds/card-slide-1.ogg',
        '/sounds/card-slide-2.ogg',
        '/sounds/card-slide-3.ogg',
        '/sounds/card-slide-4.ogg',
        '/sounds/card-slide-5.ogg',
        '/sounds/card-slide-6.ogg',
      ],
      cardPlace: [
        '/sounds/card-place-1.ogg',
        '/sounds/card-place-2.ogg',
        '/sounds/card-place-3.ogg',
        '/sounds/card-place-4.ogg',
      ],
      chipBet: [
        '/sounds/chip-lay-1.ogg',
        '/sounds/chip-lay-2.ogg',
        '/sounds/chip-lay-3.ogg',
        '/sounds/chips-collide-1.ogg',
        '/sounds/chips-collide-2.ogg',
        '/sounds/chips-collide-3.ogg',
      ],
      chipCollect: [
        '/sounds/chips-handle-1.ogg',
        '/sounds/chips-handle-2.ogg',
        '/sounds/chips-handle-5.ogg',
        '/sounds/chips-stack-1.ogg',
      ],
      check: [
        '/sounds/impactWood_light_000.ogg',
        '/sounds/impactWood_light_001.ogg',
        '/sounds/impactWood_light_002.ogg',
        '/sounds/impactWood_medium_000.ogg',
        '/sounds/impactWood_medium_001.ogg',
      ],
      fold: [
        '/sounds/card-shove-1.ogg',
        '/sounds/card-shove-2.ogg',
        '/sounds/card-shove-3.ogg',
        '/sounds/card-shove-4.ogg',
      ],
      win: [
        '/sounds/confirmation_001.ogg',
        '/sounds/confirmation_002.ogg',
      ],
      alertTurn: [
        '/sounds/switch_001.ogg',
      ]
    };

    this.preloadAll();
  }

  preloadAll() {
    if (typeof window === 'undefined') return;
    try {
      Object.values(this.soundSets).flat().forEach(src => {
        const audio = new Audio(src);
        audio.preload = 'auto';
        this.audioCache[src] = audio;
      });
    } catch (e) {
      console.warn("Pré-carregamento de áudio pausado pelo navegador:", e);
    }
  }

  setMuted(muted) {
    this.muted = muted;
  }

  isMuted() {
    return this.muted;
  }

  setVolume(vol) {
    this.volume = Math.max(0, Math.min(1, vol));
  }

  /**
   * Toca um som aleatório dentro de uma categoria com leve variação de pitch/volume
   */
  playSound(category, customVolMultiplier = 1.0, customRate = null) {
    if (this.muted) return;
    const list = this.soundSets[category];
    if (!list || list.length === 0) return;

    const randomIndex = Math.floor(Math.random() * list.length);
    const src = list[randomIndex];

    try {
      const audio = new Audio(src);
      // Taxa base: se customRate foi especificado (ex: 0.77 para durar 30% mais), usa como base
      const baseRate = customRate !== null ? customRate : 1.0;
      const pitchVar = (0.96 + Math.random() * 0.08) * baseRate;
      audio.playbackRate = pitchVar;
      audio.volume = Math.min(1, this.volume * customVolMultiplier);
      
      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playPromise.catch(() => {
          // Navegadores bloqueiam autoplay antes da primeira interação do usuário
        });
      }
    } catch (e) {
      console.warn("Erro ao reproduzir áudio:", e);
    }
  }

  // Métodos semânticos prontos para uso nos componentes
  playCardDeal() {
    this.playSound('cardSlide', 0.7);
  }

  playCommunityCard() {
    this.playSound('cardPlace', 0.9);
  }

  playChipBet() {
    this.playSound('chipBet', 0.85);
  }

  playChipWin() {
    this.playSound('chipCollect', 1.0);
    this.playSound('win', 0.8);
  }

  /**
   * Som característico de dois toques na mesa de feltro/madeira (Check clássico de poker)
   * Agora com velocidade reduzida em ~25-30% para soar mais longo/cheio (grave)
   * e intervalo humanizado de 220ms (ritmo natural de mão batendo na mesa).
   */
  playCheck() {
    // 1º toque (mais firme): rate 0.78 faz durar ~28% mais com ressonância encorpada
    this.playSound('check', 0.95, 0.78);
    setTimeout(() => {
      // 2º toque (ligeiramente mais suave, como o retorno dos nós dos dedos)
      this.playSound('check', 0.8, 0.82);
    }, 220);
  }

  /**
   * Som de cartas sendo empurradas/descartadas no feltro em direção ao muck (Fold)
   */
  playFold() {
    this.playSound('fold', 0.9);
  }

  playTurnAlert() {
    this.playSound('alertTurn', 0.8);
  }
}

export const audioEngine = new AudioEngine();
export default audioEngine;
