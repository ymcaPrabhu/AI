.PHONY: build clean zip

build:
	python src/convert.py --in input/sample.docx --template pro_report --meta config/docmeta.yaml --brand config/brand.yaml --out output/overleaf_project --build

zip:
	python src/export/pack_overleaf.py --src output/overleaf_project --zip output/overleaf_project.zip

clean:
	rm -rf output/build *.aux *.log *.out *.toc
