import random
from models import Player, Field, Ship
from restrictions import CheckSurround, BorderRestriction


class AI(Player):
    def __init__(self, turn):
        super(AI, self).__init__(turn)
        self.name = 'A.I.'

    def placing_ships_on_the_field(self, size):
        """
        With this method computer places ships on the game field
        :param size: size of the ship
        """
        old_field = list(self.field)
        upd_field = list(self.field)

        def place_ship(fld, cur_fld, trn):
            current_ship_position = set([place for place in range(
                len(fld)) if fld[place] == '&'])
            forb_places = CheckSurround(fld).forbid_placement()
            forb_places_upd = [place for place in forb_places
                               if cur_fld[place] == trn]
            if len(forb_places_upd) == 0:
                for position in current_ship_position:
                    cur_fld[position] = trn
                self.ships_alive.append(list(current_ship_position))
                return True

        commands = {'w': Ship(size).move_up,
                    'd': Ship(size).move_right,
                    's': Ship(size).move_down,
                    'a': Ship(size).move_left,
                    'r': Ship(size).rotate_ship,
                    'p': place_ship}
        while True:
            Ship(size).place_ship(old_field, upd_field)
            upd_field, old_field = list(self.field), upd_field
            attempts = 0
            randoms = random.randint(1, 50)
            try:
                while attempts != randoms:
                    commands[random.choice(('w', 'd', 's',
                                            'a', 'r'))](old_field, upd_field)
                    if BorderRestriction(upd_field).forbid_of_cross_border():
                        upd_field = list(self.field)
                        continue
                    upd_field, old_field = list(self.field), upd_field
                    attempts += 1
                if commands['p'](old_field, self.field, self.turn):
                    break
                else:
                    continue
            except IndexError:
                upd_field = list(self.field)
                continue

    def shooting(self):
        """
        Method marks the field:
        'o' - miss
        'x' - hit the target
        """
        wounded_ships = [deck for deck in range(len(
            self.opponent.field)) if self.opponent.field[deck] == 'x' and
                         self.opponent.field[deck] not in self.ships_hit]
        if len(wounded_ships) == 1:
            while True:
                shot = random.choice(list(
                    AI.shooting_area(wounded_ships)))
                if self.opponent.field[shot] == self.opponent.turn:
                    self.opponent.field[shot] = 'x'
                    break
                elif self.opponent.field[shot] is None:
                    self.opponent.field[shot] = 'o'
                    break
                else:
                    continue
        elif len(wounded_ships) > 1:
            if self.opponent.field[wounded_ships[-1] - 1] == 'x':
                while True:
                    shot = random.choice(list(
                        AI.horizontal_shooting_area(wounded_ships)))
                    if self.opponent.field[shot] == self.opponent.turn:
                        self.opponent.field[shot] = 'x'
                        break
                    elif self.opponent.field[shot] is None:
                        self.opponent.field[shot] = 'o'
                        break
                    else:
                        continue
            else:
                while True:
                    shot = random.choice(list(
                        AI.upright_shooting_area(wounded_ships)))
                    if self.opponent.field[shot] == self.opponent.turn:
                        self.opponent.field[shot] = 'x'
                        break
                    elif self.opponent.field[shot] is None:
                        self.opponent.field[shot] = 'o'
                        break
                    else:
                        continue
        else:
            available_to_shoot = random.choice([pos for pos in range(
                len(self.opponent.field)) if self.opponent.field[pos] != 'o'])
            if self.opponent.field[available_to_shoot] == self.opponent.turn:
                self.opponent.field[available_to_shoot] = 'x'
            else:
                self.opponent.field[available_to_shoot] = 'o'

    @staticmethod
    def shooting_area(ship_position):
        """
        If computer hit the target this method defies the area there it will
        tries to hit the next target
        :param ship_position: current hit ship position in the list
        """
        set_of_pos = set()
        for place in ship_position:
            if place in Field.r_upper_corner:
                set_of_pos.update({place - 1},
                                  {place + Field.num_of_lines}
                                  )
            elif place in Field.r_bottom_corner:
                set_of_pos.update({place - 1},
                                  {place - Field.num_of_lines}
                                  )
            elif place in Field.l_upper_corner:
                set_of_pos.update({place + 1},
                                  {place + Field.num_of_lines}
                                  )
            elif place in Field.l_bottom_corner:
                set_of_pos.update({place + 1},
                                  {place - Field.num_of_lines}
                                  )
            elif place in Field.right_border:
                set_of_pos.update({place - 1},
                                  {place - Field.num_of_lines},
                                  {place + Field.num_of_lines}
                                  )
            elif place in Field.left_border:
                set_of_pos.update({place + 1},
                                  {place - Field.num_of_lines},
                                  {place + Field.num_of_lines}
                                  )
            elif place in Field.upper_border:
                set_of_pos.update({place + 1},
                                  {place - 1},
                                  {place + Field.num_of_lines}
                                  )
            elif place in Field.bottom_border:
                set_of_pos.update({place + 1},
                                  {place - 1},
                                  {place - Field.num_of_lines}
                                  )
            else:
                set_of_pos.update({place + 1},
                                  {place - 1},
                                  {place - Field.num_of_lines},
                                  {place + Field.num_of_lines}
                                  )
        return set_of_pos

    @staticmethod
    def horizontal_shooting_area(ship_position):
        """
        If computer hit the target this method defies the area there it will
        tries to hit the next target (horizontally)
        :param ship_position: current hit ship position in the list
        """
        set_of_pos = set()
        for place in ship_position:
            if place in Field.r_upper_corner:
                set_of_pos.update({place - 1})
            elif place in Field.r_bottom_corner:
                set_of_pos.update({place - 1})
            elif place in Field.l_upper_corner:
                set_of_pos.update({place + 1})
            elif place in Field.l_bottom_corner:
                set_of_pos.update({place + 1})
            elif place in Field.right_border:
                set_of_pos.update({place - 1})
            elif place in Field.left_border:
                set_of_pos.update({place + 1})
            elif place in Field.upper_border:
                set_of_pos.update({place + 1},
                                  {place - 1})
            elif place in Field.bottom_border:
                set_of_pos.update({place + 1},
                                  {place - 1})
            else:
                set_of_pos.update({place + 1},
                                  {place - 1})
        return set_of_pos

    @staticmethod
    def upright_shooting_area(ship_position):
        """
        If computer hit the target this method defies the area there it will
        tries to hit the next target (upright)
        :param ship_position: current hit ship position in the list
        """
        set_of_pos = set()
        for place in ship_position:
            if place in Field.r_upper_corner:
                set_of_pos.update(
                                  {place + Field.num_of_lines}
                                  )
            elif place in Field.r_bottom_corner:
                set_of_pos.update(
                                  {place - Field.num_of_lines}
                                  )
            elif place in Field.l_upper_corner:
                set_of_pos.update(
                                  {place + Field.num_of_lines}
                                  )
            elif place in Field.l_bottom_corner:
                set_of_pos.update(
                                  {place - Field.num_of_lines}
                                  )
            elif place in Field.right_border:
                set_of_pos.update(
                                  {place - Field.num_of_lines},
                                  {place + Field.num_of_lines}
                                  )
            elif place in Field.left_border:
                set_of_pos.update(
                                  {place + Field.num_of_lines},
                                  {place - Field.num_of_lines}
                                  )
            elif place in Field.upper_border:
                set_of_pos.update(
                                  {place + Field.num_of_lines}
                                  )
            elif place in Field.bottom_border:
                set_of_pos.update(
                                  {place - Field.num_of_lines}
                                  )
            else:
                set_of_pos.update(
                                  {place - Field.num_of_lines},
                                  {place + Field.num_of_lines}
                                  )
        return set_of_pos
