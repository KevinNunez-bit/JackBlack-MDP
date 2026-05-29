"""
 Modelo de Blackjack como entorno para aprendizaje por refuerzo.

 Estado: (suma_jugador, carta_crupier, as_usable)
 Acciones: 0 = plantarse, 1 = pedir carta
 """

from random import randint

PLANTARSE = 0
PEDIR = 1


class Blackjack:

    def reparte_carta(self):
        # el 10, J, Q, K valen 10, por eso hay prob 4/13 para el valor 10
        return min(randint(1, 13), 10)

    def _mejor_suma(self, cartas):
        """Suma optima contando un as como 11 si no nos pasamos."""
        suma = sum(cartas)
        as_usable = False
        if 1 in cartas and suma + 10 <= 21:
            suma += 10
            as_usable = True
        return suma, as_usable

    def estado_inicial(self):
        """
        Reparte cartas iniciales.
        Devuelve (estado, blackjack_natural).
        """
        c1 = self.reparte_carta()
        c2 = self.reparte_carta()
        crupier = self.reparte_carta()

        suma, as_usable = self._mejor_suma([c1, c2])

        if suma == 21:
            return (21, crupier, as_usable), True  # blackjack natural

        cartas = [c1, c2]
        while suma < 12:
            cartas.append(self.reparte_carta())
            suma, as_usable = self._mejor_suma(cartas)

        return (suma, crupier, as_usable), False

    def acciones_legales(self, s):
        suma, _, _ = s
        if suma >= 21:
            return [PLANTARSE]
        return [PLANTARSE, PEDIR]

    def sucesor(self, s, a):
        """
        Devuelve el estado siguiente.
        Regresa None si el episodio termino.
        """
        suma, carta_crupier, as_usable = s

        if a == PEDIR:
            nueva = self.reparte_carta()
            nueva_suma = suma + nueva
            nuevo_as = as_usable

            if nueva_suma > 21 and nuevo_as:
                nueva_suma -= 10
                nuevo_as = False

            if nueva_suma > 21:
                return None  # bust

            return (nueva_suma, carta_crupier, nuevo_as)

        else:  # plantarse, turno del crupier
            carta_oculta = self.reparte_carta()
            mano_c = [carta_crupier, carta_oculta]
            suma_c, _ = self._mejor_suma(mano_c)

            while suma_c < 17:
                mano_c.append(self.reparte_carta())
                suma_c, _ = self._mejor_suma(mano_c)

            self._suma_crupier = suma_c
            return None  # terminal

    def recompensa(self, s, a, s_):
        suma, _, _ = s

        if a == PEDIR:
            if s_ is None:
                return -1  # bust
            return 0  # juego sigue

        else:  # plantarse
            suma_c = self._suma_crupier
            if suma_c > 21 or suma > suma_c:
                return 1  # gana el jugador
            elif suma == suma_c:
                return 0  # empate
            else:
                return -1  # gana el crupier


if __name__ == "__main__":
    juego = Blackjack()


    ganas = 0
    empates = 0
    pierdes = 0

    for _ in range(10000):
        s, blackjack = juego.estado_inicial()

        if blackjack:
            ganas += 1
            continue

        # estrategia simple: pedir si suma < 17
        while s is not None and 1 in juego.acciones_legales(s):
            suma, _, _ = s
            if suma < 17:
                a = PEDIR
            else:
                a = PLANTARSE
            s_ = juego.sucesor(s, a)
            r = juego.recompensa(s, a, s_)
            if s_ is None:
                if r == 1:
                    ganas += 1
                elif r == 0:
                    empates += 1
                else:
                    pierdes += 1
            s = s_

    print(f"Ganas:   {ganas / 100:.1f}%")
    print(f"Empates: {empates / 100:.1f}%")
    print(f"Pierdes: {pierdes / 100:.1f}%")
