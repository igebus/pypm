# coding=utf-8
from utils import datautils

database = datautils.create_database()
root = database[0]
trash = database[1]
config = database[2]

network = datautils.create_group(root, "Network")

server = datautils.create_entry(network, "Server")
server.set_username("Skryty Admin")
server.set_password("ołsaH")
server.set_comment("Pozdrawiam")


games = datautils.create_group(root, "Games")

cool_game = datautils.create_entry(games, "Cool game")
cool_game.set_username("_Xxgeneric_usernamexX_")
cool_game.set_password("P@s5w0rd")

boring_game = datautils.create_entry(games, "Boring game")
boring_game.set_username("Lorem ipsum")
boring_game.set_password("1234")


general = datautils.create_group(root, "General")

kenobi = datautils.create_entry(general, "Kenobi")
kenobi.set_username("obi-wan")
kenobi.set_password("YAPassword")
kenobi.set_comment("Hello there!")

even_more_general = datautils.create_group(general, "Even more general")

super_general = datautils.create_entry(even_more_general, "Most general entry")
super_general.set_password("abc")

example = datautils.create_entry(even_more_general, "Example")
example.set_username("example")
example.set_password("elpmaxe")
example.set_url("https://example.com")
example.set_comment("Example comment")


other = datautils.create_entry(general, "Other")
other.set_comment("Just used to store this encrypted comment for some reason")
