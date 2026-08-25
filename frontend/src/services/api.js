const API_BASE_URL = "http://127.0.0.1:8000";

async function handleResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
        data.message ||
        "Something went wrong while contacting the server."
    );
  }

  return data;
}

export async function uploadDocument(file) {
  const formData = new FormData();

  formData.append("file", file);

  try {
    const response = await fetch(
      `${API_BASE_URL}/upload`,
      {
        method: "POST",
        body: formData,
      }
    );

    return await handleResponse(response);
  } catch (error) {
    if (error.message) {
      throw error;
    }

    throw new Error(
      "Could not connect to the ResearchPilot server."
    );
  }
}

export async function askQuestion(question, document_ids = []) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/ask`,
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          question,
          document_ids,
        }),
      }
    );

    return await handleResponse(response);
  } catch (error) {
    if (error.message) {
      throw error;
    }

    throw new Error(
      "Could not connect to the ResearchPilot server."
    );
  }
}