import cli_ui

# coloring:
cli_ui.info(
  "This is",
  cli_ui.red, "red", cli_ui.reset,
  "and this is",
  cli_ui.bold, "bold"
)

# enumerating:
list_of_things = ["foo", "bar", "baz"]
for i, thing in enumerate(list_of_things):
    cli_ui.info_count(i, len(list_of_things), thing)

# progress indication:
cli_ui.info_progress("Done",  5, 20)
cli_ui.info_progress("Done", 10, 20)
cli_ui.info_progress("Done", 20, 20)

# reading user input:
with_sugar = cli_ui.ask_yes_no("With sugar?", default=False)

fruits = ["apple", "orange", "banana"]
selected_fruit = cli_ui.ask_choice("Choose a fruit", choices=fruits)

#  ... and more!