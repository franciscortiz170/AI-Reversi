import random

class Agent:
   
    symbol = 'O'
    path = "PATH TO DATA FILE"
    read_File_Data = {}
    game_States = []
    current_gameboards = []
    temp_gameboard = ("",[],"")
    iteration = 0
    turn = 0

    def __init__( self, xORo ):
        self.symbol = xORo
        self.turn = 0
        self.read_File_Data = {}
        self.current_gameboards = []
        self.game_States = []
        self.getGameStates()
        self.current_gameboards = []
        self.temp_gameboard = ("",[],"")
        self.iteration = 0

    #looks at the gameboard and returns a set of data based on it
    def readGameState(self,gameboard):
        num = 0
        data = [-1 for i in range(36)]
        newData = []
        for i in range(36):
            if gameboard[i] == '-':
                num += 1
                data[i] = i

        percent = 1/num

        for position in data:
            if position != -1:
                newData.append("(" + str(position) + ", " + str(percent) + ")")
        dataList = list(newData[len(newData)-1])
        dataList.pop()
        newData[len(newData)- 1] = "".join(dataList)
        if gameboard not in self.read_File_Data:
            self.read_File_Data[gameboard] = (newData, 0)
        return newData

    #updates the file with the new data
    def update(self): 
        lines = []
        num = 0
        for game_State in self.game_States:
            gameboard = game_State
            temp = ""
            for i in range(len(self.read_File_Data[gameboard][0])):
                temp += str(self.read_File_Data[gameboard][0][i]) + ","
            temp = temp[:-1]
            temp = temp.strip()
            if num != len(self.game_States) - 1:
                lines.append(gameboard + "," + temp + "\n")
                num += 1
            else:
                lines.append(gameboard + "," + temp)

        with open(self.path, 'w') as f:
            f.writelines(lines)
        f.close()  

    #adds a game board to the list of game boards
    def addGameBoard( self, gameboard):
        self.game_States.append((gameboard))

    #gets all the game states within our data file
    def getGameStates(self):
        self.game_States = []
        # print("getting game states")
        with open(self.path, 'r') as f:
            lines = f.readlines()
            #set up: game state, (array int, weight), (array int, weight) etc.
            for line in lines: 
                temp = line.split(',')
                self.game_States.append(temp[0])
                gameboard = temp[0]
                temp.pop(0)
                tempList = []
                i = 0
                lenght = len(temp) /2
                while len(temp) > lenght:
                    tempList.append(temp[i] + "," + temp[i+1])
                    temp.pop(i)
                    i += 1
                self.read_File_Data[gameboard] = (tempList, 0)
        f.close()

    #gives data in the form of a list of tuples
    def data(self, data_Move):
        new_Data = []
        # print("splitting data")
        for i in range(len(data_Move)):
            data_Move[i] = data_Move[i].split(',')
        # print("splitting data again")
        while len(data_Move) > 0:
            temp = data_Move[0][0].split('(')[1]
            temp = (int(temp), float(data_Move[0][1].split(')')[0]))
            data_Move.pop(0)
            new_Data += [temp]
        return new_Data

    #gives a move based on the gameboard
    def move(self, gameboard):
        # print("adding new data")
        temp_data = []
        if gameboard in self.read_File_Data:
            new_Data = self.data(self.read_File_Data[gameboard][0])
        else:
            new_Data = self.data(self.readGameState(gameboard))
        index = 0
        max = new_Data[0]
        while True:
            randomNum = random.random()
            randomIndex = random.randint(0, len(new_Data) - 1)
            if new_Data[randomIndex][1] > randomNum:
                max = new_Data[randomIndex]
                index = randomIndex
                break
        for i in range(len(new_Data)):
            temp_data.append("(" + str(new_Data[i][0]) + "," + str(new_Data[i][1]) + ")")
        if gameboard == self.temp_gameboard[0]:
            self.temp_gameboard = (gameboard, temp_data, index)
        self.read_File_Data[gameboard] = (temp_data, index)
        return max[0], index

    #this edits the data based on a loss
    def editDataLoss(self, data, index, turn):
        data = self.data(data)
        move = data[index][0]
        temp_data = []
        if len(data) == 1:
            data[index] = (move, 1.0)
        elif turn == 0:
            new_Percent = 0.0
            spread = data[index][1]/(len(data) - 1)
            data[index] = (move, new_Percent)
        else:
            percent = data[index][1]
            spread = 0.0
            new_Percent = percent/(2 + turn - 1)
            spread = new_Percent/(len(data) - 1)
            data[index] = (move, percent - new_Percent)
        for i in range(len(data)):
            if i != index:
                if data[i][1] + spread > 1:
                    data[i] = (data[i][0], 1.0)
                else:
                    data[i] = (data[i][0], data[i][1] + spread)
            temp_data.append("(" + str(data[i][0]) + "," + str(data[i][1]) + ")")
        data = temp_data
        return data

    #this edits the data based on a win
    def editDataWon(self, data, index, turn):
        data = self.data(data)
        move = data[index][0]
        temp_data = []
        if len(data) == 1:
            data[index] = (move, 1.0)
        if turn == 0:
            new_Percent = 1.0
            spread = 1.0
            data[index] = (move, new_Percent)
        else:
            percent = data[index][1]
            new_Percent = percent + (percent/(2**(turn - .6)))
            if new_Percent >= 1:
                new_Percent = 1.0
                spread = 1.0
            else:
                spread = new_Percent/(len(data) - 1)
            data[index] = (move, new_Percent)
        for i in range(len(data)):
            if i != index:
                if data[i][1] - spread < 0:
                    data[i] = (data[i][0], 0.0)
                else:
                    data[i] = (data[i][0], data[i][1] - spread)
            temp_data.append("(" + str(data[i][0]) + "," + str(data[i][1]) + ")")
        data = temp_data
        return data

    #this edits the data based on a tie
    def editDataTie(self, data, index, turn):
        data = self.data(data)
        move = data[index][0]
        temp_data = []
        if len(data) == 1:
            data[index] = (move, 1.0)
        else:
            percent = data[index][1]
            new_Percent = percent/(2**(turn - .8))
            spread = new_Percent/(len(data) - 1)
            data[index] = (move, percent - new_Percent)
        for i in range(len(data)):
            if i != index:
                if data[i][1] + spread > 1:
                    data[i] = (data[i][0], 1.0)
                else:
                    data[i] = (data[i][0], data[i][1] + spread)
            temp_data.append("(" + str(data[i][0]) + "," + str(data[i][1]) + ")")
        data = temp_data
        return data

    #this is to edit data based on if a move was not possible
    #as of right now it is not used but will worked on after phase 2
    def editData(self, moves, index):
        data = self.data(moves)
        percent = data[index][1]
        temp_data = []
        spread = 0
        if percent > 0:
            spread = percent/10
            data[index] = (data[index][0], percent - spread)
        for i in range(len(data)):
            if data[i][1] + spread >= 1:
                data[i] = (data[i][0], 1.0)
            elif i != index:
                data[i] = (data[i][0], data[i][1] + spread)
            temp_data.append("(" + str(data[i][0]) + "," + str(data[i][1]) + ")")
        data = temp_data
        return data

    #the game is lost so we can begin to edit the data based on the gameboards used in game
    def gameLost(self):
        #reverse the gameboards so we can edit the data from the end of the game to the beginning
        gameboards = self.current_gameboards[::-1]
        turn = 0
        for gameboard in gameboards:
            self.read_File_Data[gameboard[0]] = (self.editDataLoss(gameboard[1], gameboard[2], turn), gameboard[2])
            turn += 1

    #game is won so we can begin to edit the data based on the gameboards used in game
    def gameWon(self):
        #reverse the gameboards so we can edit the data from the end of the game to the beginning
        gameboards = self.current_gameboards[::-1]
        turn = 0
        for gameboard in gameboards:
            self.read_File_Data[gameboard[0]] = (self.editDataWon(gameboard[1], gameboard[2], turn), gameboard[2])
            turn += 1

    #game is tied so we can begin to edit the data based on the gameboards used in game
    def gameTie(self):
        #reverse the gameboards so we can edit the data from the end of the game to the beginning
        gameboards = self.current_gameboards[::-1]
        turn = 0
        for gameboard in gameboards:
            self.read_File_Data[gameboard[0]] = (self.editDataTie(gameboard[1], gameboard[2], turn), gameboard[2])
            turn += 1

    #Gives a move to make based on the current gameboard
    def getMove( self, gameboard ):
        move , index = self.move(gameboard)
        # when the gameboard is new we added it to our game states
        if gameboard not in self.game_States:
            # print("new gameboard")
            # print("added data")
            self.addGameBoard(gameboard)
            # print("added gameboard")
            self.read_File_Data[gameboard] = (self.readGameState(gameboard), index)
            self.temp_gameboard = (gameboard, self.readGameState(gameboard), index)
            # print("added to read file data")
            # self.read_File_Data[self.temp_gameboard[0]] = (self.editData(self.read_File_Data[self.temp_gameboard[0]][0], self.temp_gameboard[2]), self.temp_gameboard[2])
            # temp_move, temp_index = self.move(self.temp_gameboard[0])
            # self.read_File_Data[self.temp_gameboard[0]] = (self.read_File_Data[self.temp_gameboard[0]][0], temp_index)
        #the previous move made is a possible for the preivous gameboard
        # if move == -1:
        #     # print("getting move")
        #     move , index = self.move(gameboard)
        #if the previous game board is the same as the current game board then we are assuming the previous move maded was not possible
        elif self.temp_gameboard[0] == gameboard:
            # print("same gameboard")
            self.iteration = 0
        if self.iteration == 1:
            # print("next")
            self.iteration = 0
            self.current_gameboards.append(self.temp_gameboard)
            self.turn += 1
            self.temp_gameboard = (gameboard, self.readGameState(gameboard), index)
        self.iteration += 1
        return move

    def endGame( self, status, gameboard):
        # learn from the result... ?
        self.current_gameboards.pop(0)
        if status == 1: 
            # you won the game
            # self.gameWon()
            p = 1
        elif status == -1:
            # you lost the game
            # self.gameLost()
            p = -1
        else: # status == 0
            # no winner
            # self.gameTie()
            p = 0
        self.current_gameboards = []
        self.turn = 0

    def stopPlaying( self ):
        # update the file with the new data
        # self.update()
        self.game_States = []

# def test():
#     agent = Agent("O")
#     agent.getGameStates()
#     print(len(agent.game_States))

# test()

