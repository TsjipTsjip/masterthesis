.PHONY: clean all

main = Victorvan Herel2025_Thesis
sources = Victorvan Herel2025_Thesis.tex sections/*.tex
includes = 

Victorvan Herel2025_Thesis.pdf : $(sources) $(includes) 
	pdflatex Victorvan Herel2025_Thesis.tex

all:
	pdflatex $(main)
	bibtex $(main)
	pdflatex $(main)
	pdflatex $(main)

clean: 
	rm -f *.toc
	rm -f *.pdf
	rm -f *.out
	rm -f *.lot
	rm -f *.log
	rm -f *.lof
	rm -f *.brf
	rm -f *.blg
	rm -f *.aux
