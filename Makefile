.PHONY: all, run, clean

all:  mainwindow.py run

run:  
	./qtpynances.py

mainwindow.py:  mainwindow.ui
	pyside-uic mainwindow.ui > mainwindow.py

clean:
	rm -f mainwindow.py
 
# DO NOT DELETE
