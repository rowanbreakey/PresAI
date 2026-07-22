import { useState, useRef, useEffect } from 'react';
import {Document, Page, pdfjs} from 'react-pdf';

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

import 'react-pdf/dist/Page/TextLayer.css';
import 'react-pdf/dist/Page/AnnotationLayer.css';

function PresentationArea({children}) {
    const [presentation, setPresentation] = useState(null);
    const [pdfData, setPdfData] = useState(null);
    const [page, setPage] = useState(1);
    const [maxPages, setMaxPages] = useState(1);
    const [containerWidth, setContainerWidth] = useState(null);
    
    const containerRef = useRef(null);
    const fileInputRef = useRef(null);

    useEffect(() => {
        if (!containerRef.current) {
            return;
        }
        
        const observer = new ResizeObserver((entries) => {
            for (let entry of entries) {
                setContainerWidth(entry.contentRect.width);
                console.log(containerWidth)
            }
        });

        observer.observe(containerRef.current);

        return () => {
            observer.disconnect();
        };
    }, [pdfData]);

    const incrementPage = () => {
        if (page < maxPages) {
            setPage((prev) => prev++);
        }
    }

    const decrementPage = () => {
        if (page > 1) {
            setPage((prev) => prev--);
        };
    }

    function selectButtonClicked() {
        fileInputRef.current.click();
    }

    function presentationUploaded(event) {
        const file = event.target.files[0];
        const reader = new FileReader();

        reader.onload = e => {
            setPdfData(e.target.result);
        }

        reader.readAsDataURL(file);
        setPresentation(file);
    }

    function onLoad({maxPages}) {
        setMaxPages(maxPages);
        setPage(1);
    }

    return(
        <>
            <input type="file" accept="application/pdf" ref={fileInputRef} onChange={presentationUploaded} style={{display:"none"}}/>
            {presentation ? (
                <div className="ratio ratio-16x9 bg-dark rounded-4 shadow overflow-hidden" ref={containerRef}>
                    <Document file={presentation} onLoadSuccess={onLoad}>
                        <Page pageNumber={page} width={containerWidth}>
                            {children}
                        </Page>
                    </Document>
                </div>
            ) : (
                <button onClick={selectButtonClicked} className="ratio ratio-16x9 bg-dark rounded-4 shadow">
                    {children}
                </button>
            )}
        </>
    )
};

export default PresentationArea;