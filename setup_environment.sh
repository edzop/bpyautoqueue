current_dir=`pwd`

#ln -s -i $current_dir/blqaf.sh /usr/bin/blqaf
#ln -s -i $current_dir/blq.sh /usr/bin/blq

echo "python3 $current_dir/render_db.py \"\$@\"" > /usr/bin/blq
chmod +x /usr/bin/blq

echo "python3 $current_dir/bake_db.py \"\$@\"" > /usr/bin/blb
chmod +x /usr/bin/blb
