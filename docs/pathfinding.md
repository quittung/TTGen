# Pathfinding
In this doc I will try to outline how I implemented the pathfinding, at least the part that I already understand.

## Infrastructure
Information about the infrastructure is stored in the data/signals folder:
 - Signal (list)
   - Signal reachable by going forward (list)
   - Signal reachable by turning around (only in station)
This data is loaded and connected to form a network. A pair of consecutive signals forms a signal path.

### Example
Let's imagine a simple station with two platforms and a double track line connected to one side.
```
A     L
1>   --->
2>   <---
```
In this case there would be four entries for this station:
 - Platform A1 (`1>`)
 - Platform A2 (`2>`)
 - Entry signal from line L (`<---`)
 - First track signal on line L (`--->`)

Signal `1>` would list Signal `--->` as a possible next signal. If there was another physical line connected to the same side of the station, its first track signal would also be added to this list. 
If there was a Signal `<1`, it would be listed as a reverse option for `1>`. 

## Processing for each line
When line (as in service) data is read and validated, the signal network is used to find every possible combination of departure and arrival tracks for every stop. That data is then checked for connectivity.

### Example
Let's say we have a line that runs between station `A` to `C`, stopping at `B` on the way.
```
A - B - C
```
Maybe `A` has two tracks, and `B` has 3.
```
 A       B
<1> ---  1>
<2> --- <2>
        <3
```

In this case we could 
 - depart from `A1`, arrive at `B1`
 - depart from `A1`, arrive at `B2`
 - depart from `A2`, arrive at `B1`
 - depart from `A2`, arrive at `B2`

This process would be repeated for every stop of the line. Then we would have to check that these paths are actually connected. 
Maybe there is no way of getting to `C` from `B1`. In that case we'd remove every path between `A` and `B` ending on `B1`.

### Problems
At this point we should be able to choose any destination signal from our list, but there I think there is an issue. Some stations might be connected by two parallel physical lines. Say a track for express trains, and another one for metro trains.
```
 A         B         C         D         E         F
 1>  ---   1>  ---   1>  ---   1>  ---   1> 
<2   ---  <2   ---  <2   ---  <2   ---  <2
           3>  ---   3>  ---   3>  -------------   3>
          <4   ---  <4   ---  <4   -------------  <4
```

Let's assume changing from the express track to the metro track is not possible after `B`. In that case it would be a simple split after `B`, which is already detected. 

But what if it is possible to change just before `D`? In that case there are two valid routing options: 
 - Go from either track at `B1` via `C1` to `D1`
 - Go from either track at `B3` via `C3` to `D1`

For now I'd prefer to be able to change any part of the routing info without causing a chain reaction. The format should be "at signal `X` chose then `n`th option out of the target signal list. But if it's possible to go to both `B1` and `B2`, the list of next signals would change. 
I'd have to generate and maintain a tree of branching decisions instead of just a list. I don't want to deal with that complexity yet, so I choose not to support infrastructure configurations like that at this point.