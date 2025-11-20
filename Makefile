MAIN = tex/main

all: pdf

pdf:
latexmk -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex

clean:
latexmk -C $(MAIN).tex

veryclean: clean
rm -f $(MAIN).pdf
