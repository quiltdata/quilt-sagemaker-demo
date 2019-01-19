#!/bin/bash
if [[ "$1" = train ]]
then
    jupyter nbconvert --execute --ExecutePreprocessor.timeout=-1 --to notebook --inplace build.ipynb
else
    python -c "import t4; t4.Package.install('aleksey/fashion-mnist-clf', registry='s3://alpha-quilt-storage', dest='.')"
    cp aleksey/fashion-mnist-clf/clf.h5 clf.h5
    rm -rf aleksey/
    python -m flask run --host=0.0.0.0 --port=8080
fi
