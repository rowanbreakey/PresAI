import { useState } from 'react';
import {Document, Page, pdfjs} from 'react-pdf';

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

import 'react-pdf/dist/Page/TextLayer.css';
import 'react-pdf/dist/Page/AnnotationLayer.css';

function PresentationArea({children}) {
    const [presentation, setPresentation] = useState(null);
    const [page, setPage] = useState(1);

    const incrementPage = () => {
        setPage((prev) => prev++);
    }

    const decrementPage = () => {
        setPage((prev) => prev--);
    }

    function selectPresentation() {
        console.log("yippee");
    }
    return(
        <>
            {presentation ? (
                <button onClick={incrementPage} className="ratio ratio-16x9 bg-dark rounded-4 shadow">
                    {children}
                </button>
            ) : (
                <button onClick={selectPresentation} className="ratio ratio-16x9 bg-dark rounded-4 shadow">
                    {children}
                </button>
            )}
        </>
    )
}

export default PresentationArea