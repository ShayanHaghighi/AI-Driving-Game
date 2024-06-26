# AI-Driving-Game

## Description

This program trains a Neural Network to play a driving game.

The `main.py` program uses the pygame library to implement the driving game, complete with drifting mechanics. The `agent.py` program uses Deep Q Learning to iteratively improve a Neural Network model, making the AI better at the driving game. The logic of the Neural Network is found in `model.py`, and the models are stored in the `/model` folder.

## Installation

1. Clone the repository
2. [Install Python](https://www.python.org/downloads/)
3. Install requirements using pip:
```
pip install -r requirements.txt
```

## Running the project

1. Navigate to the root of the project
2. Run
```python
python main.py
```
to run the Deep Q Learning Algorithm on the game.

**Or**

```python
python game.py
```
to play the driving game yourself

## Additional Information

Feel free to change the hyperparameter values (found in lines 11 in `main.py`) of the Deep Q Learning model, and in the Agent class on line 43 of `model.py`

## Questions or Feedback?

If you have any questions, encounter any issues, or have feedback to share, please don't hesitate to [open an issue](https://github.com/ShayanHaghighi/AI-Driving-Game/issues/new/choose) <!--or [reach out to me](link_to_contact_information)-->. Your input is invaluable and helps improve this project!

## Thank You

Thank you for visiting this project and for your interest in its development. Your support means a lot! If you find this project useful, consider giving it a ⭐️ or sharing it with others who might enjoy from it.

Happy coding!
