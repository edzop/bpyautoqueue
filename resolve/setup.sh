export RESOLVE_SCRIPT_API="/opt/resolve/Developer/Scripting"
export RESOLVE_SCRIPT_LIB="/opt/resolve/libs/Fusion/fusionscript.so"
#export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"

export PYTHONPATH="$PYTHONPATH:/opt/resolve/Developer/Scripting/Modules"

echo $PYTHONPATH

python3 test.py