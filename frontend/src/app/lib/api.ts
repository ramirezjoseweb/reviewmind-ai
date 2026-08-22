const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"; 

export type Business = {
    id: number; 
    name: string; 
    category: string; 
    location: string | null;
    created_at: string;  
}; 

export type BusinessCreate = {
    name: string;
    category: string; 
    location?: string;
};

export type ReviewCreate = {
    text: string; 
    rating?: number; 
    author?: string; 
    source?: string; 
    language?: string; 
}; 

export type AnalysisSummary = {
    business_id: number; 
    total_reviews: number; 
    analyzed_reviews: number; 
    positive_reviews: number; 
    negative_reviews: number; 
    neutral_reviews: number; 
    average_sentiment_score: number; 
    top_positive_aspects: string[]; 
    top_negative_aspects: string[]; 
}; 

export type Review = {
    id: number; 
    business_id: number; 
    text: string; 
    rating : number | null;
    author: string | null; 
    source: string | null; 
    language: string | null; 
    created_at: string; 
}; 

export type ReviewImportResult = {
    imported_reviews: number;  
    skipped_rows: number; 
    errors: string[]; 
}; 

async function handleResponse<T>(response: Response): Promise<T> {
    if(!response.ok) {
        const errorBody = await response.json().catch(() => null); 
        const errorMessage = 
            errorBody?.detail ?? `HTTP error ${response.status}`; 

        throw new Error(errorMessage); 
    }

    if(response.status == 204) {
        return undefined as T; // los endpoints DELETE suelen devolver 204 No Content
    }

    return response.json() 
}

export async function getBusinesses(): Promise<Business[]> {
    const response = await fetch(`${API_URL}/businesses`); 
    return handleResponse<Business[]>(response);
}

export async function createBusiness(
    business: BusinessCreate
): Promise<Business> {
    const response = await fetch(`${API_URL}/businesses`, {
        method: "POST",  
        headers: {
            "Content-Type": "application/json", 
        }, 
        body: JSON.stringify(business), 
    }); 

    return handleResponse(response); 
}

export async function createReview(
    businessId: number, 
    review: ReviewCreate
): Promise<void> {
    const response = await fetch(`${API_URL}/businesses/${businessId}/reviews`, {
        method: "POST", 
        headers: {
            "Content-Type": "application/json", 
        }, 
        body: JSON.stringify(review), 
    }); 

    await handleResponse(response);
}

export async function runAnalysis(
    businessId: number, 
): Promise<void> {
    const response = await fetch(
        `${API_URL}/businesses/${businessId}/analysis/run`, 
        {
            method: "POST", 
        }
    ); 

    await handleResponse(response) 
}

export async function getAnalysisSummary(
    businessId: number, 
): Promise <AnalysisSummary> {
    const response = await fetch(`${API_URL}/businesses/${businessId}/analysis/summary`); 
    
    return handleResponse(response) 
}

export async function getReviews(
    businessId: number, 
): Promise<Review[]> {
    const response = await fetch(
        `${API_URL}/businesses/${businessId}/reviews`
    )
    return handleResponse(response) 
}

export async function deleteBusiness(
    businessId: number
): Promise<void> {
    const response = await fetch(`${API_URL}/businesses/${businessId}`, {
        method: "DELETE", 
    }); 

    await handleResponse<void>(response);  
}

export async function deleteReview(
    businessId: number, 
    reviewId: number
): Promise<void> {
    const response = await fetch(`${API_URL}/businesses/${businessId}/reviews/${reviewId}`, {
        method: "DELETE", 
    }); 

    await handleResponse<void>(response); 
}

export async function importReviewCsv(
    businessId: number, 
    file: File
): Promise<ReviewImportResult> {
    const formData = new FormData(); 
    formData.append("file", file); 

    const response = await fetch(
        `${API_URL}/businesses/${businessId}/reviews/import-csv`, 
        {
            method: "POST", 
            body: formData, 
        }
    ); 

    return handleResponse<ReviewImportResult>(response); 
}