#!/usr/bin/perl
print+(Fizz)[$_%3].(Buzz)[$_%5]||$_,$/for 1..<>
