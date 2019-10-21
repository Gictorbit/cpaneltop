#! /usr/bin/bash

echo "creating cpaneltop directory in ~/.locale/share/ ..."
mkdir -p "$HOME/.local/share/cpaneltop"

echo "copy app directory to cpaneltop directory ..."
cp -rv "./app" "$HOME/.local/share/cpaneltop"

chmod +x "$HOME/.local/share/cpaneltop/app/cpaneltop.py"

echo "make symbolic link for cpaneltop.py"
sudo ln -s "$HOME/.local/share/cpaneltop/app/cpaneltop.py" "/usr/local/bin/cpaneltop"
