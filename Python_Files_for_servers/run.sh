#./run.sh S 0.2 Ls 1.2

proj_file="Initial_State.aedt"

var_val=()
var_name=()
i=1
for arg in "$@";
do
    if (( $i % 2 ));
    then
      var_name+=($arg)
    else
      var_val+=($arg)
    fi
  ((i++))
done

for index in ${!var_name[*]};
do
  var=${var_name[$index]}
  val=${var_val[$index]}
  echo "$var=$val"
  sed -i "s/^$var=.*$/$var=$val/" change_var.py
  sed -i "s/^$var=.*$/$var=$val/" save_s.py
done

ansysedt -ng -monitor -runscriptandexit change_var.py $proj_file
ansysedt -batchsolve -ng -monitor $proj_file
ansysedt -ng -monitor -runscriptandexit save_s.py $proj_file
