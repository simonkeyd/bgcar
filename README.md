# BGCAR

__Baldur's Gate Computer Assisted Reroll__ helps one effortlessly reach high ability scores for one's CHARNAME by performing computer assisted reroll. This program performs live roll result analysis and only stores the highest value. This is done by capturing screen area containing the `total roll` score and by analyzing this value using OCR.

## Installation
Installing from PyPI:
```sh
pip install bgcar
```

Installing from source:
```sh
git clone https://github.com/simonkeyd/bgcar && cd ${_##*/}
pip install -r requirements.txt
```

## Step by step guide
1. Start Baldur's Gate or Baldur's Gate 2 in windowed mode
1. Proceed to create your character and stop at ability page
1. Run `bgcar` (for first time use add `-i` parameter)
1. For first time use follow the initial wizard to provide the different positions that the program needs.  
Click on corresponding buttons when asked to and mark the area of the `Total roll` score by first clicking on the top left of this score and then on the bottom right.  
5. Let the program perform the rolls and stop it by pressing 't' when done

note: Baldur's Gate game window has to be in the foreground so that `bgcar` can perform capture and clicks.

## Advanced usage
```sh
usage: bgcar [-h] [-i] [-d DELAY] [-m MAX_ROLL_COUNT] [--gpu]

options:
  -h, --help            show this help message and exit
  -i, --initialize      initialize required settings like button location - mandatory before program use
  -d DELAY, --delay DELAY
                        time in second to wait between each click (one can use decimal values); a delay too short for you setup might cause program to misbehave (eg. not
                        store roll correctly)
  -m MAX_ROLL_COUNT, --max-roll-count MAX_ROLL_COUNT
                        limit the maximum number of roll that you want the program to perform; by default bgcar will run in infinite mode
  --gpu                 enable GPU mode for OCR and accelerating program
```

## Known issues
Invalid value results (eg. program finding incorrect value for a `Total roll`) can be caused by the following:
* `Total roll` score area too big or too small
* too poor game resolution
* too small game window (or both)

To prevent this from happening try re-initializing `Total roll` area (using `-i` parameter) or enlarging game window and increasing game resolution.
