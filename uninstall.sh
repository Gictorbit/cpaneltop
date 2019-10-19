if [ -d "$HOME/.local/share/cpaneltop" ] then;
    rm -rf $HOME/.local/share/cpaneltop
else
    echo "there is no cpaneltop directory in ~/.local/share"
fi

sudo unlink /usr/local/bin/cpaneltop