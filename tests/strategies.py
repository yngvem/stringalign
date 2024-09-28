import hypothesis.strategies as st


@st.composite
def different_text_strings(draw):
    # Generate the first string
    first_string = draw(st.text())
    # Generate the second string, ensuring it's different from the first
    second_string = draw(st.text().filter(lambda x: x != first_string))
    return first_string, second_string
