use unicode_segmentation::*;
use std::borrow::Cow;
use pyo3::prelude::*;


#[pyclass]
struct GraphemeClusterIterator {
    cursor: GraphemeCursor,
    data: Cow<'static, str>,
    current_index: usize,
}


#[pymethods]
impl GraphemeClusterIterator {
    #[new]
    #[pyo3(signature = (s, extended=true, /))]
    fn new(s: String, extended: bool) -> Self {
        GraphemeClusterIterator {
            cursor: GraphemeCursor::new(0, s.len(), extended),
            data: Cow::Owned(s),
            current_index: 0,
        }
    }

    fn _get_next_boundary(&mut self, current_index: usize) -> Option<usize> {
        let next_index: Result<Option<usize>, GraphemeIncomplete> = self.cursor.next_boundary(&self.data, current_index);

        match next_index {
            Ok(Some(next_index)) => Some(next_index),
            _ => None,
        }
    }

    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<'_, Self>) -> PyResult<Option<String>> {
        let current_index = slf.current_index.clone();
        let next_boundary = slf._get_next_boundary(current_index);

        match next_boundary {
            Some(next_index) => {
                let out = slf.data[slf.current_index..next_index].to_string();
                slf.current_index = next_index;
                Ok(Some(out))
            }
            None => Ok(None),
        }
    }
}


#[pyfunction]
#[pyo3(signature = (s, extended=true, /))]
fn grapheme_clusters(s: &str, extended: bool) -> PyResult<Vec<&str>> {
    // let chars: Vec<char> = s.chars().collect();
    let g = UnicodeSegmentation::graphemes(s, extended).collect::<Vec<&str>>();

    Ok(g)
}


#[pymodule]
fn _stringutils(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(grapheme_clusters, m)?)?;
    m.add_class::<GraphemeClusterIterator>()?;

    Ok(())
}
