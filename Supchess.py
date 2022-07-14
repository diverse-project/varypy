import chess as c,random as r
w=True
pk=[5,5,5,5,3]
while(w):
    s=[r.randrange(0,64) for i in range(0,5)]
    b=c.Board(fen=None)
    for q in range(0,5):b.set_piece_at(s[q],c.Piece(pk[q],w))
    if len(set()|(*[list(b.attacks(s[q]))for q in range(0,5)],s))>63:break