extensions [ sound ]

globals [ notes major-steps modenames coordinates notecoords  ourorange ourgreen ouryellow ourswapcolor ourpink basekeyval notenums playnotes playpentanotes harmonicanotes modifications?  notedict  pentnotedict]

breed [ holes hole ]
breed [ labelers labeler ]

breed [ swappers swapper ]
holes-own [ my-note ]

to startup
  setup
end

to setup
  ca
  ;import-drawing "charmonica.png"
  setup-notes
  reset-ticks
  set ourorange [ 255 130 0 130 ]
  set ourgreen  [ 0 255 0 100 ]
  set ouryellow [ 255 255 0 100 ]
  set ourswapcolor [ 0 255 255 180 ]
  set ourpink [ 75 75 255 128 ]
  set modifications? false
  get-notes-for
end

to setup-notes
  set notes [ "C" "Db" "D" "Eb" "E" "F" "Gb" "G" "Ab" "A" "Bb" "B" ]
  let initnote position harmonicakey notes
  ifelse initnote < 7 [ set basekeyval 60 + initnote ] [ set basekeyval  60 - (12 - initnote) ]
  set notes (sentence (sublist notes initnote (length notes)) (sublist notes 0 initnote))
  set harmonicanotes (sentence notes notes notes notes)
  show (word harmonicakey "harmonica.png")
  import-drawing (word harmonicakey "harmonica.png")
  set major-steps [ 0 2 4 5 7 9 11 ]
  set notenums map [ x -> x + basekeyval ] [0 1 2 3 4 5 6 7 8 9 10 11]
  set modenames [ "major" "dorian" "phryigian" "lydian" "mixalydian" "minor" "locrian" ]
;  set major 0
;  set dorian 1
;  set phrygian 2
;  set lydian 3
;  set mixalydian 4
;  set minor 5
;  set locrian 6
  set coordinates [[-6.9 -2.41] [-6.9 0.1] [-6.95 1.14] [-6.9 2.23] [-5 -2.41] [-5 -0.7] [-5 0.1] [-5 1.14] [-3.15 -2.41] [-3.15 -1.39] [-3.15 -0.7] [-3.15 0.1] [-3.15 1.14] [-1.2 -2.41] [-1.2 0.1] [-1.2 1.14] [-1.2 2.29] [0.75 -2.41] [0.75 1.14] [0.75 2.2] [2.65 -2.41] [2.65 0.1] [2.65 1.14] [2.65 2.23] [4.55 -2.41] [4.55 1.14] [4.55 2.29] [6.5 -3.53] [6.5 -2.41] [6.5 1.14] [8.4 -3.53] [8.4 -2.41] [8.4 1.14] [8.4 2.23] [10.3 -4.37] [10.3 -3.53] [10.3 -2.41] [10.3 1.14] [10.3 2.23]]
  set notecoords [0 1 2 3 4 5 6 7 7 8 9 10 11 0 1 2 3 4 5 6 7 8 9 10 0 11 1 3 4 2 6 7 5 8 10 11 0 9 1]
  make-note-turtles
  ask holes [ ht ]
end


to change-harmonica
end

to make-note-turtles
  let directions (map sentence coordinates notecoords)
  foreach directions
  [
    dir ->
    create-holes 1
    [
      setxy item 0 dir item 1 dir
      set my-note item (item 2 dir) notes
      ;set label my-note
      ;set label-color blue
      set shape "rect"
      set color [255 0 0 100]
      set size 1.9  ;1.9
    ]
  ]
  create-labelers 1 [ setxy 10 4.9  set label-color white  set shape "circle" set size .25 set color black]
end

to-report index-of [ n ]
  report n mod 12
end

to-report note [ n ]
  report item (index-of n) notes
end

to-report num-for-key [ name ]
  let p position name notes
  let q ""
  if member? "#" name [ set q "Use flat versus sharp notation." ]
  ifelse p = false [user-message (word "No note: " name ". " q) report false ]
  [ report p ]
end

to-report num-for-mode [ modename ]
  let p position modename modenames
  let q ""
  if member? "#" modename [ set q "Use flat versus sharp notation." ]
  ifelse p = false [user-message (word "No mode: " modename ". " q) report false ]
  [ report p ]
end

to-report get-major-scale-for [name]
  let to-return []
  let n num-for-key name
  let i 0
  while [i < length major-steps]
  [
    let noten (n + item i major-steps)
    let next note noten
    set to-return lput next to-return
    set i i + 1
  ]
  report to-return
end


to get-notes-for
  let answer []
  set playnotes []
  let shiftsteps num-for-mode mode
  let shifttoparentscale item shiftsteps major-steps
  let basekeynum ((num-for-key key) - (shifttoparentscale)) mod 12
  let basekey item basekeynum notes
  show (word "Base key " basekey)
  let thenotes get-major-scale-for basekey
  let shift position key thenotes
  let i 0
  while [i < length thenotes]
  [
    let noten (shift + i) mod (length thenotes)
    let next item noten thenotes
    show next
    set answer lput next answer
    set i i + 1
  ]
  show (word "***" answer)

  if not modifications?
  [
    ask holes [ht set color ouryellow ]
    foreach answer
    [
      n ->
      ask holes with [ my-note = n ] [ st ]
    ]


    ask holes with [ my-note = first answer ] [ set color ourgreen ]
    if member? mode [ "major" "dorian" "phryigian" ]
    [ ask holes with [my-note = item 3 answer or my-note = item 6 answer][ set color ourorange ] ]
    if member? mode [ "lydian" "mixalydian" "minor" "locrian" ]
    [ ask holes with [my-note = item 1 answer or my-note = item 5 answer][ set color ourorange ] ]
  ]

  set playnotes []
  set playpentanotes []
  set notedict []
  set pentnotedict []
  let tempharmonicanotes harmonicanotes
  let zro position (first answer) tempharmonicanotes
  let indx 0
  while [ indx < zro ]
  [
   set tempharmonicanotes replace-item indx tempharmonicanotes "Z"
   set indx indx + 1
  ]
  foreach answer
  [
    n ->
    let m position n tempharmonicanotes
    let note-to-add (basekeyval + position n tempharmonicanotes)
    set notedict lput (list n m note-to-add) notedict
    set playnotes lput note-to-add playnotes
    if [color] of one-of holes with [ my-note = n ] != ourorange [
      set playpentanotes lput note-to-add playpentanotes
      set pentnotedict lput (list n  m note-to-add) pentnotedict
    ]
    set tempharmonicanotes replace-item m tempharmonicanotes "Z"
    ;show tempharmonicanotes
  ]

  let finishoctavenote position (first answer) tempharmonicanotes
  set playnotes lput (basekeyval + finishoctavenote) playnotes
  set notedict lput (list (first answer) finishoctavenote (basekeyval + finishoctavenote)) notedict

  set playpentanotes lput (basekeyval + finishoctavenote) playpentanotes
  set pentnotedict lput (list (first answer) finishoctavenote (basekeyval + finishoctavenote)) pentnotedict

  ask labelers [ set label (word key " " mode)  ]
  show (word " ^^^ " notedict)
  show (word " &&& " pentnotedict)
end


to play [ alist ]
  foreach alist
  [
    n ->
    sound:start-note "harmonica" last n 64
    let reserve-color 0
    let holenum item 1 n
    ask one-of holes with [ my-note = (first n)] [ set reserve-color color ]
    ask holes with [ my-note = (first n) and (who >= holenum) and (who < holenum + 2)][ set color ourpink ]
    ;show holenum
    ;ask hole holenum [
    ;  set reserve-color color
    ;  set color ourpink
    ;]
    display
    wait note-length
    sound:stop-note "harmonica" last n
    ask holes with [ my-note = (first n) ][ set color reserve-color ]
    ;ask hole holenum [ set color reserve-color ]
  ]
end



to swap-notes
  if mouse-down?
  [
    let startswap nobody
    let endswap nobody
    set startswap min-one-of holes with [hidden? = false and (color = ouryellow or color = ourorange) ] [distancexy mouse-xcor mouse-ycor]
    ifelse [ distancexy mouse-xcor mouse-ycor ] of startswap < 1
    [
      let swapicon nobody
      create-swappers 1 [
        set shape "arrow"
        set color ourswapcolor
        set swapicon self
      ]
      while [ mouse-down? ]
      [

        ask swapicon [
          if mouse-xcor != xcor or mouse-ycor != ycor  [ facexy mouse-xcor mouse-ycor ]
          setxy mouse-xcor mouse-ycor
        ]
      ]
      set endswap min-one-of holes with [hidden? = false and (color = ouryellow or color = ourorange)] [distancexy mouse-xcor mouse-ycor]
      ask swapicon [ die ]
      ifelse [ distancexy mouse-xcor mouse-ycor ] of endswap < 1
      [
        show (word "Would swap " [my-note] of startswap " with " [my-note] of endswap)
        let col [color] of startswap
        ask holes with [ my-note  = [my-note] of startswap ] [ set color [color] of endswap ]
        ask holes with [ my-note  = [my-note] of endswap ] [ set color col ]
        set modifications? true
        get-notes-for
        ask labelers [
          if not member? "Modified" label
          [
            set label (word "Modified " label)
          ]
        ]
      ]
      [
        user-message "You didn't drag to a valid swap location"
      ]
    ]
    [
       user-message "You didn't drag from a valid note to swap. (You can't swap out the root note.)"
    ]
  ]
end




to do-export-logic
  ifelse user-yes-or-no? ( word "EXPORT view as: " [label] of one-of labelers  ".png")
  [
    export-view (word [label] of one-of labelers  ".png")
  ]
  [
    let f user-input "What filename?"
    if f != false [ export-view (word f ".png") ]
  ]
end
@#$#@#$#@
GRAPHICS-WINDOW
210
10
1308
540
-1
-1
47.4
1
30
1
1
1
0
1
1
1
-11
11
-5
5
0
0
1
ticks
30.0

BUTTON
41
161
172
211
Show Layout
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

CHOOSER
39
66
172
111
key
key
"C" "Db" "D" "Eb" "E" "F" "Gb" "G" "Ab" "A" "Bb" "B"
5

CHOOSER
39
114
173
159
mode
mode
"major" "dorian" "phryigian" "lydian" "mixalydian" "minor" "locrian"
1

BUTTON
1207
545
1309
578
Export Map
do-export-logic
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

CHOOSER
38
17
173
62
HarmonicaKey
HarmonicaKey
"C" "D" "E" "F" "G" "A" "Bb"
0

MONITOR
20
232
198
277
mode's notes
playnotes
17
1
11

BUTTON
50
282
170
315
play mode
play notedict ;playnotes
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

MONITOR
22
376
194
421
mode's 'pentatonic' notes
playpentanotes
17
1
11

BUTTON
23
422
194
455
play 'pentatonic' mode
play pentnotedict ;playpentanotes
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SLIDER
22
507
194
540
note-length
note-length
.1
1
0.3
.1
1
sec
HORIZONTAL

BUTTON
31
320
201
353
play mode descending
play reverse notedict  ;playnotes
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
14
459
202
492
'pentatonic' mode descending
play reverse pentnotedict  ;playpentanotes
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
383
541
554
574
NIL
swap-notes
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
701
542
847
575
NIL
sound:stop-music
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

TEXTBOX
854
543
1067
576
In case the sound extension gets 'stuck,' you an press this to shut it up!
11
0.0
1

@#$#@#$#@
## WHAT IS IT?

(a general understanding of what the model is trying to show or explain)

## HOW IT WORKS

(what rules the agents use to create the overall behavior of the model)

## HOW TO USE IT

(how to use the model, including a description of each of the items in the Interface tab)

## THINGS TO NOTICE

(suggested things for the user to notice while running the model)

## THINGS TO TRY

(suggested things for the user to try to do (move sliders, switches, etc.) with the model)

## EXTENDING THE MODEL

(suggested things to add or change in the Code tab to make the model more complicated, detailed, accurate, etc.)

## NETLOGO FEATURES

(interesting or unusual features of NetLogo that the model uses, particularly in the Code tab; or where workarounds were needed for missing features)

## RELATED MODELS

(models in the NetLogo Models Library and elsewhere which are of related interest)

## CREDITS AND REFERENCES

(a reference to the model's URL on the web if it has one, as well as any other necessary credits, citations, and links)
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

rect
false
0
Rectangle -7500403 true true 16 79 301 226

rectold
false
0
Rectangle -7500403 true true 0 75 315 225

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.3.0
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
