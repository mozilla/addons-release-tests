filenames=tests/frontend/test_*.py
for file in $filenames; do
  filename=$(basename $file)
  echo $filename >> test_frontend_filenames.txt
done