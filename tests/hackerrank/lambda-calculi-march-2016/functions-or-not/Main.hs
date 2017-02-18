module Main where
import Control.Applicative
import Control.Monad
import Data.List

isFunction :: Int -> [(Int, Int)] -> Bool
isFunction n = (== n) . length . nub . sort . map fst

main :: IO ()
main = do
    t <- readLn
    replicateM_ t $ do
        n <- readLn
        r <- replicateM n $ do
            [x, y] <- map read . words <$> getLine
            return (x, y)
        putStrLn (if isFunction n r then "YES" else "NO")
