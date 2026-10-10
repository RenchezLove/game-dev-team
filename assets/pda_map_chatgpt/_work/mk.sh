# usage: mk.sh sx sy tx ty  -> image drawn at x=tx,y=ty with size 2048*sx, 2048*sy (in schema px)
sx=$1; sy=$2; tx=$3; ty=$4
w=$(awk "BEGIN{print 2048*$sx}"); h=$(awk "BEGIN{print 2048*$sy}")
sed -e "s|<rect width=\"2048\" height=\"2048\" fill=\"#b9c48a\"/>|<rect width=\"2048\" height=\"2048\" fill=\"#000\"/><image href=\"gpt.png\" x=\"$tx\" y=\"$ty\" width=\"$w\" height=\"$h\" preserveAspectRatio=\"none\"/>|" \
 -e 's|<g fill="#7a8f4e" opacity="0.55">|<g fill="none" opacity="0">|' \
 -e 's|<rect width="2048" height="2048" fill="url(#fog)"/>||' \
 -e 's|0 0 0 0 0.55  0 0 0 0 0.38  0 0 0 0 0.20  5 0 -5 0 -2.2|0 0 0 0 0  0 0 0 0 1  0 0 0 0 1  2.5 0 -2.5 0 -1.1|' \
 -e 's|<g font-size="34"|<g display="none" font-size="34"|' -e 's|<g font-size="26"|<g display="none" font-size="26"|' scheme.html > overlay.html
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless --disable-gpu --hide-scrollbars --allow-file-access-from-files --window-size=2048,2048 --screenshot="E:\game-dev-team\assets\pda_map_chatgpt\_work\overlay.png" "file:///E:/game-dev-team/assets/pda_map_chatgpt/_work/overlay.html" 2>&1 | grep -c written
