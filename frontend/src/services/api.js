const API_BASE_URL =
  "http://127.0.0.1:8000";


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

  formData.append(
    "file",
    file
  );

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


export async function askQuestion(
  question,
  documentId,
  conversationId = null
) {

  try {

    const requestBody = {
      question,
      document_id: documentId,
    };


    // Only include conversation_id
    // for follow-up questions.
    if (conversationId !== null) {

      requestBody.conversation_id =
        conversationId;

    }


    const response = await fetch(
      `${API_BASE_URL}/ask`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
        },
        body: JSON.stringify(
          requestBody
        ),
      }
    );

    return await handleResponse(
      response
    );

  } catch (error) {

    if (error.message) {

      throw error;

    }

    throw new Error(
      "Could not connect to the ResearchPilot server."
    );

  }

}


export async function getConversation(
  conversationId
) {

  try {

    const response = await fetch(
      `${API_BASE_URL}/conversations/${conversationId}`
    );

    return await handleResponse(
      response
    );

  } catch (error) {

    if (error.message) {

      throw error;

    }

    throw new Error(
      "Could not connect to the ResearchPilot server."
    );

  }

}