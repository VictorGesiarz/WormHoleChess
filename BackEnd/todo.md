# ButtHoleChess

## Backend

- [x] Do the TODO

**Game:**
- [ ] Implement Board por 2 players (Base and Layer):
  - Should it be in the same file as the other and just changing some configuration or in a new file with the same board logic but changing the manual 
- [ ] Implement ChessFactory to easily decide what kind of game to start and set the initial positions of the pieces. 
- [ ] Implement Monte Carlo Tree Search (or at least take a good look at how it works and what I should do, for now)

**Base Board Optimization:** 

- [ ] Change order of pieces to look for checks.
- [ ] Stop searching other player movements if any of the moves makes a check.
- [ ] Look for checks from the king rather than from all the other pieces looking for the king. 
- [ ] Implement Layer Board. 
  - [x] Layer board creation
  - [ ] Layer board logic
  - [ ] Layer board tile
  - [ ] Layer board pieces
  - [ ] Layer board game

**API:**

- [ ] Implement game API
  - [ ] Game Start: it should allow for personalized boards? Or should that be in another api. 
  - [ ] Move
  - [ ] Surrender / Exit
  - [ ] ...

## Frontend 

- [ ] Connect game API: listen for socket messages (game_started, player_moved, player_eliminated, game_over, etc)
- [ ] Implement origin piece selection (the tile from which the piece will move, should be able to be selected from the tile and from the piece) and the destination of the movement. 
- [ ] Implement color highlighting of the possible moves of a piece when selected. 
- [ ] Implement timers sincronized with the backend for each player. 
- [ ] Implement player eliminated effect and game over pop up. 
- [ ] Implement movement history. 
- [ ] Let undo and redo only for visualization. 
- [ ] Implement a game editor in another page where you can put any pieces wherever you want and then 

## Documentacion

- [ ] Redactar introducción, explicación del juego, idea del TFG. 
- [ ] Diseñar dibujos 2d para hacer explicaciones de como lo he programado y que optimizaciones estoy haciendo. 