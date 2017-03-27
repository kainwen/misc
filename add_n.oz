declare DivideStream NFullAdder GateMaker FullAdder HalfAdder AndG OrG XorG Disp

proc {Disp S}
   case S
   of A|B then
      {Browse A}
      thread {Disp B} end
   else
      skip
   end
end

fun {GateMaker F}
   fun {$ Xs Ys}
      fun {GateLoop Xs Ys}
	 case Xs#Ys of (X|Xr)#(Y|Yr) then
	    {F X Y}|{GateLoop Xr Yr}
	 else
	    nil
	 end
      end
   in
      thread {GateLoop Xs Ys} end
   end
end

AndG={GateMaker fun {$ X Y} X*Y end}
OrG={GateMaker fun {$ X Y} X+Y-X*Y end}
XorG={GateMaker fun {$ X Y} X+Y-2*X*Y end}

proc {FullAdder X Y Z C S}
 A B D E F
in
 A={AndG X Y}
 B={AndG Y Z}
 D={AndG X Z}
 F={OrG B D}
 C={OrG A F}
 E={XorG X Y}
 S={XorG Z E}
end

proc {HalfAdder X Y C S}
   C = {AndG X Y}
   S = {XorG X Y}
end

fun {DivideStream S}
   proc {BindList OutStream RemStream}
      if RemStream == nil then
	 for P in OutStream do
	    case P of H|T then T = nil end
	 end
      else
	 for P in {List.zip OutStream RemStream fun {$ A B} A#B end} do
	    case P of (H|T)#B then T = B end
	 end
      end
   end
in
   case S
   of L|Sr then
      local OutStreamList RemStream in
	 thread RemStream = {DivideStream Sr} end
	 OutStreamList = {Map L fun {$ E} E|_ end}
	 thread {BindList OutStreamList RemStream} end
	 OutStreamList
      end
   else
      nil
   end
end

fun {NFullAdder S1 S2}
   As = {DivideStream S1}
   Bs = {DivideStream S2}
   AB_Pair = {List.zip As Bs fun {$ A B} A#B end}
   fun {BuildBlock AB_Pair}
      case AB_Pair
      of [A0#B0] then
	 local S0 C1 in
	    {HalfAdder A0 B0 C1 S0}
	    [C1#S0]
	 end
      [] (An#Bn)|RemPair then
	 local RemResult C S Cnb in
	    RemResult = {BuildBlock RemPair}
	    (Cnb#_)|_ = RemResult
	    {FullAdder An Bn Cnb C S}
	    (C#S)|RemResult
	 end
      end
   end
   Block = {BuildBlock AB_Pair}
   SStreamList = {Map Block fun {$ P}
			       case P of C#S then S end
			    end}
   (CStream#_)|_ = Block
   fun {MakeResult CStream SStreamList}
      if CStream == nil then
	 nil
      else L in
	 L = {Map SStreamList fun {$ S} S.1 end}
	 case CStream of C|Cr then
	    (L#C) | thread {MakeResult Cr {Map SStreamList fun {$ S} S.2 end}} end
	 end
      end
   end
in
   {MakeResult CStream SStreamList}
end

declare S1 S2 S3
S1 = [1 1 1 1 1]|[0 0 0 0 0]|[1 1 1 1 0]|_
S2 = [1 1 1 1 1]|[0 0 0 0 0]|[0 0 0 0 1]|_
S3 = {NFullAdder S1 S2}
{Browse S3}
